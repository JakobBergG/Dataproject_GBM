import os
from radiomics import featureextractor

"""
A new conda environment has been made to accommodate radiomics' need for python 3.7.12. Remember to use this interpreter inVS CODE

"""

dataDir = os.path.join(os.getcwd(), "..", "test")

imagepath = os.path.join(dataDir, "mr.gz")
labelpath = os.path.join(dataDir, "gtv.gz")

extractor = featureextractor.RadiomicsFeatureExtractor()

result = extractor.execute(imagepath, labelpath)

print("Calculated features:")
for key, value in result.iteritems():
    print(key, ":", value)