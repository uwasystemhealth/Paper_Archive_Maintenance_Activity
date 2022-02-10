from datetime import date
from owlready2 import *

import pandas as pd
import dateutil.parser as parser

bfo_onto = None
iof_annotation_onto = None
iof_core_onto = None
funtional_breakdown_onto = None
asset_list_onto = None
maintenance_activity_onto = None
work_order_onto = None
maint_activity_classification_rules_onto = None
data_onto = None
onto = None

obo = None
mar = None
al = None
ma = None
owl = None

def load_ontology():
    global bfo_onto, iof_annotation_onto, iof_core_onto, functional_breakdown_onto, asset_list_onto, maintenance_activity_onto, work_order_onto, maint_activity_classification_rules_onto, onto
    global obo, mar, ma, al, owl
    onto_path.append('../v2')
    bfo_onto = get_ontology("bfo-v2.owl").load()
    iof_annotation_onto = get_ontology("iof_AnnotationsVocabulary.rdf").load()
    iof_core_onto = get_ontology("IOF.owl").load()
    functional_breakdown_onto = get_ontology("functional-breakdown-pump-ontology.owl").load()
    asset_list_onto = get_ontology("asset-list-ontology.owl").load()
    work_order_onto = get_ontology("work-order-ontology.owl").load()
    maintenance_activity_onto = get_ontology("maintenance-activity.owl").load()
    maint_activity_classification_rules_onto = get_ontology("activity-classification-rules.owl").load()
    onto = get_ontology("data.owl").load()

    obo = bfo_onto.get_namespace("http://purl.obolibrary.org/obo/")
    mar = onto.get_namespace("http://www.semanticweb.org/maintenance-activity-classification-rules#")
    al = asset_list_onto.get_namespace('http://www.semanticweb.org/asset-list-ontology#')
    ma = maintenance_activity_onto.get_namespace('http://www.semanticweb.org/maintenance-activity#')
    owl = onto.get_namespace('http://www.w3.org/2002/07/owl#')
    print('loaded')

def load_data(input_data_sheet_path):
    # Read excel data into dataframe
    return pd.read_excel(input_data_sheet_path)

def populate(data_frame):
    print("Populating Ontology")

    for index, row in data_frame.iterrows():

        mwo_name = "MWO-"+str(row['ID'])
        date = add_work_order_created_date_individual(row, mwo_name)
        work_order = add_work_order_description_individual(row, mwo_name)
        func_loc = add_functional_location_tag_individual(row, mwo_name)
        labor = add_labour_cost(row, mwo_name)
        material = add_material_cost(row, mwo_name)
        maint_type = add_maintenance_type(row, mwo_name)
        activity = add_activity_individual(row, mwo_name)
        #wo_execution_event = add_wo_execution_event(row, mwo_name, activity)

        with onto:
            mwo = mar.Maintenance_Work_Order_Record(mwo_name)
            AllDifferent([mwo, date, work_order, func_loc, labor, material, maint_type, activity])
            mwo.has_data_field.append(date)
            mwo.has_data_field.append(work_order)
            mwo.has_data_field.append(func_loc)
            mwo.has_data_field.append(labor)
            mwo.has_data_field.append(material)
            mwo.has_data_field.append(maint_type)
            mwo.has_data_field.append(activity)
       
        # todo: figure out why allDifferent is not working
    
def add_work_order_created_date_individual(row, mwo_name):
    date_name = mwo_name+"_created_date"
    date_value =  parser.parse(row['Date']).isoformat()
    with onto:
        date = mar.work_order_created_date(date_name)
        date.hasValue.append(date_value) # todo: figure out how to make a date type
        return date

def add_work_order_description_individual(row, mwo_name):
    description_name = mwo_name+"_description"
    description_value = row['Unstructured Text']
    with onto:
        description = mar.work_order_description_text(description_name)
        description.hasValue.append(description_value)
        description.nlpIdentifiedItem.append(al.Motor) # todo: complete these
        description.nlpIdentifiedActivity.append(row['NLP Identified Activity'])
        item_string = format_item(row['NLP Identified Item'])
        description.nlpIdentifiedItem.append('http://www.semanticweb.org/asset-list-ontology#'+item_string)
        return description

def format_item(item_string):
        return "".join(x.capitalize() or ' ' for x in item_string.split(" "))

def add_functional_location_tag_individual(row, mwo_name):
    functional_location_tag_name = mwo_name+"_functional_location_tag"
    functional_location_tag_value = "TBD" # todo: figure out what's going on here
    with onto:
        functional_location_tag = mar.work_order_functional_location_tag(functional_location_tag_name)
        functional_location_tag.hasValue.append(functional_location_tag_value)
        return functional_location_tag

def add_labour_cost(row, mwo_name):
    labour_cost_name = mwo_name+"_labour_cost"
    labour_cost_value = row['Labor Cost']
    with onto:
        labour_cost = mar.work_order_labour_cost(labour_cost_name)
        labour_cost.hasValue.append(labour_cost_value)
        return labour_cost

def add_material_cost(row, mwo_name):
    material_cost_name = mwo_name+"_material_cost"
    material_cost_value = row['Material Cost']
    with onto:
        material_cost = mar.work_order_material_cost(material_cost_name)
        material_cost.hasValue.append(material_cost_value)
        return material_cost

def add_maintenance_type(row, mwo_name):
    maintenance_type_name = mwo_name+"_maintenance_type"
    maintenance_type_value = row['Work Order Type']
    with onto:
        maintenance_type = mar.work_order_maintenance_type(maintenance_type_name)
        maintenance_type.hasValue.append(maintenance_type_value)
        return maintenance_type

def add_activity_individual(row, mwo_name):
    activity_name = mwo_name+"_activity"
    with onto:
        activity = owl.Thing(activity_name)
        activity.is_a.append(Or([ma.MaintenanceActivity, ma.SupportingActivity]))
        activity.is_a.remove(activity.is_a[0]) # hack to create activity without owl:Thing
        return activity

#def add_wo_execution_event(row, mwo_name, activity):
#    wo_execution_event_name = mwo_name+"_wo_execution_event"
#    with onto:
#        wo_execution_event = onto.work_order_execution_event(wo_execution_event_name)
#        wo_execution_event.BFO_0000057.append(activity)
#        return wo_execution_event

def save_ontology():
    print("Saving Ontology")
    onto.save(file = "../v2/populated-data.owl", format = "rdfxml")

def main():
    print("Starting Population Script")
    input_data_sheet_path = "data.xlsx"
    load_ontology()
    data_frame = load_data(input_data_sheet_path)
    populate(data_frame)
    save_ontology()
if __name__ == "__main__":
    main()
