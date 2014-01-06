from nupic.engine import *
import json

class ImageClassifier():
	""" Classifies images based on training data """
	
	def buildNetwork(self, architecture):
		""" Take a dictionary that represents the architecture and build
			it into a complete network. Returns a nupic.engine.Network network

			architecture: (dict) describing the architecture. must have the keys:
				regions: (list of dictionaries). each dictionary must have
					name: (string) the identifier
					type: (string) the type of region eg "py.ImageSensor"
					params: (dict) parameters to be passed
				links: (list of dictionaries) each dictionary must have
					src: (string) the name of the source region
					dest: (string) the name destination region
					type: (string) default type of link. usually "UniformLink"
					terminals: (list of dicts) each dictionary must have
						srcOutput: (string) the output of the source to connect
						destInput: (string) the input on the source to connect
						params: (dict) (optional) parameters specific to this link
						type: (string) (optional) override type in higher level
					params: (dict) parameters common to all links between the regions. can be overriden. 
		"""

		self.net = Network()
		
		for region in architecture["regions"]:
			self.net.addRegion(str(region["name"]), str(region["type"]), json.dumps(region["params"]))

		for link in architecture["links"]:
			for terminal in link["terminals"]:
				linkType = link["type"]
				params = link["params"]
				if "type" in terminal: linkType = terminal["type"]
				if "params" in terminal:
					for key, val in terminal["params"].iteritems():
						params[key] = val
				self.net.link(str(link["src"]), str(link["dest"]), str(linkType), json.dumps(params), str(terminal["srcOutput"]), str(terminal["destInput"]))

		self.net.initialize()
		return self.net

	def _loadImages(self, directory, additionalArgs=[]):
		""" load all images in directory and its subdirs into the ImageSensor
			and return the number of network steps it will take to explore
			all images. """
		requiredIterations = 0
		for name in self.net.regions:
			if self.net.regions[name].type != "py.ImageSensor": continue
			args = ["loadMultipleImages", directory]+additionalArgs
			self.net.regions[name].executeCommand(args)
			nn = self.net.regions[name].getParameter("numIterations")
			if nn > requiredIterations: requiredIterations = nn
		return requiredIterations

	def train(self, trainingDir, imageLoadingArgs=[]):
		requiredIterations = self._loadImages(trainingDir, imageLoadingArgs)
		self.net.run(requiredIterations)

	def test(self, testingDir):
		pass

	def __init__(self, architecturePath):
		self.architecturePath = architecturePath
		architectureFile = open(architecturePath, 'r')
		self.buildNetwork(json.load(architectureFile))

def main():
	classifier = ImageClassifier("architecture.json")
	classifier.train("../nupic-vision-data/faces-v-motorbikes")

if __name__ == '__main__':
	main()