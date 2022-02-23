
from owlready2 import *
from typing import List

def query_not_matching(world):
    """SPARQL query to find non-matching activity types"""

    query = """
    PREFIX bfo:<http://purl.obolibrary.org/obo/>
    PREFIX core:<http://www.industrialontologies.org/core/>
    PREFIX activity:<http://www.semanticweb.org/maintenance-activity#>
    PREFIX work:<http://www.semanticweb.org/work-order-ontology#>
    PREFIX macr:<http://www.semanticweb.org/maintenance-activity-classification-rules#>
    SELECT DISTINCT ?activity ?clazz ?nlpActivityType
    WHERE {
        ?activity a/rdfs:subClassOf* macr:InferredActivity ;
            a ?clazz .
        FILTER isIRI( ?clazz )
        FILTER ( ?clazz != macr:InferredActivity && ?clazz != macr:UncertainActivity && ?clazz != macr:MaintenanceSupportingOrUnspecifiedActivity )
        # FILTER NOT EXISTS { ?activity a/rdfs:subClassOf* macr:UncertainActivity } 
        FILTER NOT EXISTS { ?activity a/rdfs:subClassOf* macr:InferredActivityTypeMatchesWorkOrderDescription }
        OPTIONAL {
            ?activity core:describedBy|^core:describes ?_record .
            ?_record work:refersTo ?nlpActivityType .
            ?nlpActivityType rdfs:subClassOf+ activity:MaintenanceActivity . 
                # a/rdfs:subClassOf* activity:replace .
        }
    }
    """
    results = world.sparql(query)
    return [r for r in results if not isinstance(r[1], int) ] # filter the extraneous references to the number '12'

def query_records_and_classifications(world):
    """
    SPARQL query for retreiving the record details plus the resolved activity type and activity classification
    """

    query = """
    PREFIX bfo:<http://purl.obolibrary.org/obo/>
    PREFIX core:<http://www.industrialontologies.org/core/>
    PREFIX activity:<http://www.semanticweb.org/maintenance-activity#>
    PREFIX work:<http://www.semanticweb.org/work-order-ontology#>
    PREFIX macr:<http://www.semanticweb.org/maintenance-activity-classification-rules#>
    SELECT DISTINCT ?record ?tag_name ?tagged_item ?text ?activity ?item ?unit ?labour_cost ?material_cost ?date_time ?maint_type ?activityType ?nlpActivityRef
    WHERE {
        ?record a work:MaintenanceWorkOrderRecord ;
            work:hasDataField ?_tag ;
            work:hasDataField ?description ;
            work:hasDataField ?labour ;
            work:hasDataField ?material ;
            work:hasDataField ?date ;
            work:hasDataField ?_maint_type .
        ?_tag a work:WorkOrderFunctionalLocationTag ;
            work:refersTo ?tagged_item .
        OPTIONAL {
            ?_tag work:hasValue ?tag_name ;
        }
        ?description a work:WorkOrderDescriptionText ;
            work:hasValue ?text ;
            macr:nlpIdentifiedActivity ?activity ;
            macr:nlpIdentifiedItem ?item ;
            macr:nlpIdentifiedSubunit ?unit .
        ?labour a work:WorkOrderLabourCost ;
            work:hasValue ?labour_cost .
        ?material a work:WorkOrderMaterialCost ;
            work:hasValue ?material_cost .
        ?date a work:WorkOrderCreatedDate ;
            work:hasValue ?date_time .
        ?_maint_type a work:WorkOrderMaintenanceType ;
            a ?maint_type .
        ?maint_type rdfs:subClassOf work:WorkOrderMaintenanceType .
        OPTIONAL {
            ?record core:describes ?_activity .
            ?_activity a ?activityType .
            ?activityType rdfs:subClassOf+ activity:MaintenanceActivity .
        }
        OPTIONAL {
            ?description work:refersTo ?nlpActivityRef .
            ?nlpActivityRef rdfs:subClassOf+ activity:MaintenanceActivity .
        }
    }
    """
    results = world.sparql(query)
    return list(results)

def simplify_results(results : List[List[ThingClass]]) -> List[List[str]]:
    """Reduces the owlready2 objects to short name strings"""
    return [[ o.name if hasattr(o, 'name') else str(o) for o in r ] for r in results ]

def main(first_record=1, last_record=36):
    """Run the reasoning. We process each record individually due to issues with the tooling.
    """
    print('Reasoning over records', first_record, 'to', last_record)

    owlready2.reasoning.JAVA_MEMORY = 4000
    onto_path.append('../imports')
    onto_path.append('../data')
    onto_path.append('../')

    classifications = []
    results = []
    records = []

    for i in range(first_record - 1, last_record):
        print('Processing record', i + 1)
        the_world = World()
        onto = the_world.get_ontology(f"../data/populated-data-{i}.owl").load(only_local=True)
        data = onto.get_namespace('http://www.semanticweb.org/data#')
        rules = onto.get_namespace('http://www.semanticweb.org/maintenance-activity-classification-rules#')
        activity = onto.get_namespace('http://www.semanticweb.org/maintenance-activity#')
        work_order = onto.get_namespace('http://www.semanticweb.org/work-order-ontology#')
        func_breakdown = onto.get_namespace('http://www.semanticweb.org/functional-breakdown-pump-ontology#')
        asset_classes = onto.get_namespace('http://www.semanticweb.org/asset-list-ontology#')

        with onto:
            sync_reasoner_pellet(the_world, infer_property_values=True, 
                infer_data_property_values=True)
            if len(data[f'MWO-{i + 1}_activity'].is_a) <= 2:
                # Reasoning didn't run properly, no new classifications discovered. Run again as amazingly it works sometimes...
                sync_reasoner_pellet(the_world, infer_property_values=True, 
                infer_data_property_values=True)
        
        i_results = query_not_matching(the_world)
        results.extend(simplify_results(i_results))
        r_results = query_records_and_classifications(the_world)
        records.extend(simplify_results(r_results))
        classifiers = simplify_results([data[f'MWO-{i + 1}_activity'].is_a])
        classifications.append( (f'MWO-{i + 1}_activity', classifiers[0]) )

    print(classifications)
    print(results)
    print(records)


if __name__ == '__main__':
    # quick and dirty args handling
    args = [int(arg) for arg in sys.argv[1:]]
    main(*args)


