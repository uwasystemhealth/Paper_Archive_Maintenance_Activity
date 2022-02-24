# Paper Archive: Maintenance Activity Ontology

This is a working repository for work associated with the Maintenance Activity Ontology. This ontology has been submitted for review.

This work is authored by: Caitlin Woods, Matt Selway, Tyler Bikaun, Markus Stumptner and Melinda Hodkiewicz.

This repository contains the following folders:
- __data__: OWL files containing instance data, populated using the population_script.
- __imports__: OWL files used as imports in the maintenance activity ontologies.
- __population_script__: A python script to regenerate the files contained in the data folder.
- __reasoning_script__: A python script to perform reasoning in the ontology.

The file, __maintenance-activity.owl__, contains the _maintenance activity reference ontology_ presented in the paper.

The files, __maintenance-activity-classification-rules.owl__, __asset-data.owl__, __asset-list-ontology.owl__, __functional-breakdown-pump-ontology.owl__, and __work-order-ontology.owl__, contain data files necesarry for running the _application level ontology for maintenance work order data quality_. 

## Notes on the Reasoning Script

For initial testing of the ontology, the goal was to use easily accessible tools and the python `owlready2` library with the Pellet reasoner was chosen.
This combination has some limitations, including the time taken to perform the reasoning over the entire dataset; hence, the dataset was split into individual files for each Maintenance Work Order Record.

The reasoning script can be run across all records, and individual record, or some subset of records. For example, running

```
reasoning_script> python runner.py
```

will run the full set (1-36), while

```
reasoning_script> python runner.py 3 12
```

will run the third to twelfth records. The last argument can be omitted to run until the end, e.g., third to 36th record if omitted from the above example.
Finally, the following would run only the second record:

```
reasoning_script> python runner.py 2 2
```

There is also some inconsistency in the output occasionally (exact cause is unknown) where the activity classifications are not inferred and so the script will run the pellet reasoner twice if it detects such an occurrence.

Lastly, the punning of the annotation properties (which should be fine as it only puns each annotation property to a data property or object property but not both) could lead to inconsistent reasoning output (sometimes it would work and other times not) and, hence, has been excluded from the data files for reliability of the script.

These issues appear to be idiosyncratic of the tools being used in this instance.
