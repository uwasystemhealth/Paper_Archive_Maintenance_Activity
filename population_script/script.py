from datetime import date
from numpy import place
from owlready2 import *
import sys

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
wo = None
core = None

pump_number = '001'


def load_ontology():
    global bfo_onto, iof_annotation_onto, iof_core_onto, functional_breakdown_onto, asset_list_onto, maintenance_activity_onto, work_order_onto, maint_activity_classification_rules_onto, onto
    global obo, mar, ma, al, owl, wo, core
    onto_path.append('../v2/imports')
    bfo_onto = get_ontology("bfo-v2.owl").load()
    iof_annotation_onto = get_ontology(
        "IOF_AnnotationsVocabulary.rdf").load()
    iof_core_onto = get_ontology("IOF.owl").load()
    onto_path.append('../v2')
    functional_breakdown_onto = get_ontology(
        "functional-breakdown-pump-ontology.owl").load()
    asset_list_onto = get_ontology("asset-list-ontology.owl").load()
    work_order_onto = get_ontology("work-order-ontology.owl").load()
    maintenance_activity_onto = get_ontology("maintenance-activity.owl").load()
    maint_activity_classification_rules_onto = get_ontology(
        "activity-classification-rules.owl").load()
    onto = None
    onto = get_ontology("data.owl").load()

    obo = bfo_onto.get_namespace("http://purl.obolibrary.org/obo/")
    mar = onto.get_namespace(
        "http://www.semanticweb.org/maintenance-activity-classification-rules#")
    al = asset_list_onto.get_namespace(
        'http://www.semanticweb.org/asset-list-ontology#')
    ma = maintenance_activity_onto.get_namespace(
        'http://www.semanticweb.org/maintenance-activity#')
    owl = onto.get_namespace('http://www.w3.org/2002/07/owl#')
    wo = work_order_onto.get_namespace(
        'http://www.semanticweb.org/work-order-ontology#')
    core = iof_core_onto.get_namespace(
        'http://www.industrialontologies.org/core/')
    print('loaded')


def load_data(input_data_sheet_path):
    # Read excel data into dataframe
    return pd.read_excel(input_data_sheet_path)


def populate_single(index, row):
    print('populating index + ' + str(index))
    # sub_unit_indiv = select_sub_unit(row['NLP Identified Subunit'])
    item_indiv = select_item(row['NLP Identified Item'])

    mwo_name = "MWO-"+str(row['ID'])
    date = add_work_order_created_date_individual(row, mwo_name)
    work_order = add_work_order_description_individual(row, mwo_name)
    func_loc = add_functional_location_tag_individual(
        row, mwo_name, item_indiv)
    labor = add_labour_cost(row, mwo_name)
    material = add_material_cost(row, mwo_name)
    maint_type = add_maintenance_type(row, mwo_name)
    activity = add_activity_individual(row, mwo_name)
    wo_execution_event = add_wo_execution_event(
        row, mwo_name, activity, item_indiv)

    with onto:
        mwo = mar.Maintenance_Work_Order_Record(mwo_name)
        AllDifferent([mwo, date, work_order, func_loc, labor,
                      material, maint_type, activity, wo_execution_event])
        mwo.has_data_field.append(date)
        mwo.has_data_field.append(work_order)
        mwo.has_data_field.append(func_loc)
        mwo.has_data_field.append(labor)
        mwo.has_data_field.append(material)
        mwo.has_data_field.append(maint_type)
        mwo.describes.append(activity)
        mwo.describes.append(wo_execution_event)
        mwo.isInputOfAtSomeTime.append(wo_execution_event)


def populate(data_frame):
    print("Populating Ontology")

    for index, row in data_frame.iterrows():

        # sub_unit_indiv = select_sub_unit(row['NLP Identified Subunit'])
        item_indiv = select_item(row['NLP Identified Item'])

        mwo_name = "MWO-"+str(row['ID'])
        date = add_work_order_created_date_individual(row, mwo_name)
        work_order = add_work_order_description_individual(row, mwo_name)
        func_loc = add_functional_location_tag_individual(
            row, mwo_name, item_indiv)
        labor = add_labour_cost(row, mwo_name)
        material = add_material_cost(row, mwo_name)
        maint_type = add_maintenance_type(row, mwo_name)
        activity = add_activity_individual(row, mwo_name)
        wo_execution_event = add_wo_execution_event(
            row, mwo_name, activity, item_indiv)

        with onto:
            mwo = mar.Maintenance_Work_Order_Record(mwo_name)
            AllDifferent([mwo, date, work_order, func_loc, labor,
                         material, maint_type, activity, wo_execution_event])
            mwo.has_data_field.append(date)
            mwo.has_data_field.append(work_order)
            mwo.has_data_field.append(func_loc)
            mwo.has_data_field.append(labor)
            mwo.has_data_field.append(material)
            mwo.has_data_field.append(maint_type)
            mwo.describes.append(activity)
            mwo.describes.append(wo_execution_event)
            mwo.isInputOfAtSomeTime.append(wo_execution_event)


def select_sub_unit(sub_unit):
    individual_map = [
        ['control and monitoring', 'pump_'+pump_number+'_control_and_monitoring'],
        ['lubrication', 'pump_'+pump_number+'_lub_system'],
        ['pump unit', 'pump_'+pump_number+'unit'],
        ['driver and electrical', 'pump_'+pump_number+'_driver_system'],
        ['power transmission', 'pump_'+pump_number+'_power_transmission'],
        ['piping and valves', 'pump_'+pump_number+'_piping_system'],
    ]
    # get first column from 2d array
    index = [x[0] for x in individual_map].index(sub_unit)
    return individual_map[index][1]


def select_item(item):
    individual_map = [
        ['oil', 'oil_'+pump_number],
        ['flowmeter', 'flow_meter_'+pump_number],
        ['pump', 'pump_'+pump_number],
        ['pressure switch', 'pressure_switch_'+pump_number],
        ['valve', 'valve_'+pump_number],
        ['motor', 'motor_'+pump_number],
        ['mechanical seal', 'seal_'+pump_number],
    ]
    index = [x[0] for x in individual_map].index(item)
    return individual_map[index][1]


def add_work_order_created_date_individual(row, mwo_name):
    date_name = mwo_name+"_created_date"
    input_date = parser.parse(row['Date']).isoformat()
    date_value = ""
    date_value = datetime.datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S")
    with onto:
        date = mar.work_order_created_date(date_name)
        # todo: figure out how to make a date type
        date.hasValue.append(date_value)
        return date


def add_work_order_description_individual(row, mwo_name):
    description_name = mwo_name+"_description"
    description_value = row['Unstructured Text']
    with onto:
        description = mar.work_order_description_text(description_name)
        description.hasValue.append(description_value)
        description.nlpIdentifiedActivity.append(
            row['NLP Identified Activity'])
        item_string = format_item(row['NLP Identified Item'])
        description.nlpIdentifiedItem.append(al[item_string])
        sub_unit_string = format_item(row['NLP Identified Subunit']) + "System"
        if (sub_unit_string == "LubricationSystem"):
            description.nlpIdentifiedSubunit.append(
                al[sub_unit_string])  # todo: ask Matt about this
        else:
            description.nlpIdentifiedSubunit.append(mar[sub_unit_string])
        return description


def format_item(item_string):
    return "".join(x.capitalize() or ' ' for x in item_string.split(" "))


def add_functional_location_tag_individual(row, mwo_name, item):
    functional_location_tag_name = mwo_name+"_functional_location_tag"
    with onto:
        functional_location_tag = mar.work_order_functional_location_tag(
            functional_location_tag_name)
        functional_location_tag.refers_to.append(onto[item])
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
        maintenance_type_value_string = 'work_order_' + \
            maintenance_type_value+'_maintenance'
        maintenance_type = mar.work_order_maintenance_type(
            maintenance_type_name)
        maintenance_type = mar[maintenance_type_value_string](
            maintenance_type_name)
        return maintenance_type


def add_activity_individual(row, mwo_name):
    activity_name = mwo_name+"_activity"
    with onto:
        activity = owl.Thing(activity_name)
        activity.is_a.append(
            Or([ma.MaintenanceActivity, ma.SupportingActivity]))
        # hack to create activity without owl:Thing
        activity.is_a.remove(activity.is_a[0])
        return activity


def add_wo_execution_event(row, mwo_name, activity, item):
    wo_execution_event_name = mwo_name+"_wo_execution_event"
    with onto:
        wo_execution_event = wo.WorkOrderExecutionProcess(
            wo_execution_event_name)
        wo_execution_event.BFO_0000117.append(activity)
        wo_execution_event.BFO_0000057.append(onto[item])
        return wo_execution_event


def save_ontology(filename):
    onto.save(file=filename, format="rdfxml")


def main():
    print("Starting Population Script")
    input_data_sheet_path = "data.xlsx"

    data_frame = load_data(input_data_sheet_path)

    i = int(sys.argv[1])  # cannot loop because of owlready caching.

    for index, row in data_frame.iterrows():
        if index == i:  # must do one at a time because owlready caching

            load_ontology()  # reload ontology each run.
            populate_single(index, row)
            save_ontology("../v2/populated-data-"+str(index)+".owl")

    # populate(data_frame)


if __name__ == "__main__":
    main()


# notes:
# - lubrication system in wrong place
# - pump unit system does not exist under engineered system
# - what to do with func loc refers to.
