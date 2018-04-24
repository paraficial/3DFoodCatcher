import numpy
import math
import glm
from GLContext import *

# Helper functions
def vec3(x, y, z): return numpy.array([x, y, z])

def perspective(fovy, aspect, zNear, zFar):
	tanHalfFovy = math.tan(fovy/2)
	matrix = numpy.array([
		[1/(aspect * tanHalfFovy),0,0,0],
		[0,(1/tanHalfFovy),0,0],
		[0,0,-((zFar+zNear)/(zFar-zNear)),-1],
		[0,0,-((2*zFar*zNear)/(zFar-zNear)),0]])
	return matrix.transpose()

def normalize(v):
	absolute = numpy.linalg.norm(v)
	if absolute != 0:
		return v/absolute
	else:
		return v

def lookAt(eye, center, up):
	f = normalize(center - eye)
	u = normalize(up)
	s = normalize(numpy.cross(f, u))

	matrix = numpy.array([
		[s[0], u[0], -f[0], 0],
		[s[1], u[1], -f[1], 0],
		[s[2], u[2], -f[2], 0],
		[-numpy.dot(s, eye), -numpy.dot(u, eye), numpy.dot(f, eye), 1]])
	return  matrix.transpose()

def scaleMatrix(value):
	matrix = numpy.array([[value,0,0,0], [0,value,0,0], [0,0,value,0], [0,0,0,1]])
	return matrix

def translationMatrix(v):
	matrix = numpy.array([[1,0,0,v[0]], [0,1,0,v[1]], [0,0,1,v[2]], [0,0,0,1]])
	return matrix

def rotationMatrixZ(angle):
	matrix = numpy.array([[math.cos(angle), -math.sin(angle), 0, 0], [math.sin(angle), math.cos(angle), 0, 0], [0,0,1,0], [0,0,0,1]])
	return matrix

def rotationMatrixY(angle):
	matrix = numpy.array([[math.cos(angle), 0, -math.sin(angle), 0], [0, 1, 0, 0], [math.sin(angle), 0, math.cos(angle), 0], [0,0,0,1]])
	return matrix

identityMat = numpy.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])

# Classes
# A mesh contains the data for drawing
class Mesh:
	def __init__(self, meshFilename):

		# Parsing custom .mesh fileformat
		self.vertexData = []
		self.indices = []
		with open(meshFilename, 'r') as meshFile:
			for line in meshFile:
				sLine = line.split()
				if not len(sLine):
					continue
				if sLine[0] == "v":
					self.vertexData = self.vertexData + sLine[1:]
				if sLine[0] == "indices":
					self.indices = self.indices + sLine[1:]

		self.vertexData = numpy.array(self.vertexData, dtype=numpy.float32)
		self.indices = numpy.array(self.indices, dtype=numpy.uint32)

		# OpenGL related calls
		self.vao = glGenVertexArrays(1)
		self.vbo = glGenBuffers(1)
		self.ibo = glGenBuffers(1)

		glBindVertexArray(self.vao)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
		glBufferData(GL_ARRAY_BUFFER, self.vertexData, GL_STATIC_DRAW)

		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

		glEnableVertexAttribArray(0)
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
		glBindVertexArray(0)
	
	def printData(self):
		for v in self.vertexData:
			print(v)
		print(self.indices)
	
	def draw(self, shader):
		glUseProgram(shader)
		glBindVertexArray(self.vao)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
		glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
		glBindVertexArray(0)
		glUseProgram(0)
		
# A bot is going to have a neural network and can be trained to harvest food.
# Currently it's behaving more like a solar system...
class Bot:
	"""
	The neural net gets 2 vectors (6 floats) as input: current speed, and direction to food.
	Output is 1 vector (3 floats) which will be its acceleration.
	It has to learn how to accelerate correctly to get its food.
	It won't grow.
	"""
	def __init__(self):
		# Rendering
		self.mesh = Mesh("meshes/cube.mesh")
		self.scale = 2
		self.modelMatrix = scaleMatrix(self.scale) @ translationMatrix(vec3(-0.5, -0.5, 0.0))
		self.color = vec3(0.0, 0.2, 0.8)
		
		# Physics
		self.position = vec3(0,0,0)
		self.velocity = vec3(0,0,0)
		self.acceleration = vec3(0,200,0)
		
		# Brain
		# to be continued...

	def draw(self, shader):
		self.updatePosition()
		
		# Apply movement
		glUseProgram(shader)
		glUniformMatrix4fv(glGetUniformLocation(shader, "modelMatrix"), 1, GL_TRUE, self.modelMatrix)
		glUniform3fv(glGetUniformLocation(shader, "color"), 1, self.color)
		glUseProgram(0)

		self.mesh.draw(shader)
	
	def updatePosition(self):
		self.modelMatrix = scaleMatrix(self.scale) @ translationMatrix(self.position) @ translationMatrix(vec3(-0.5, -0.5, -0.5))
	
	def calcPhysics(self, timeStep, direction):
		self.acceleration = direction # fake brain output
		
		self.velocity = self.velocity + self.acceleration * timeStep
		self.position = self.position + self.velocity * timeStep
		
		# Reset acceleration to zero and decrease velocity
		#self.acceleration = vec3(0,0,0)
		#self.velocity = 0.9 * self.velocity
		

# The food is positioned randomly and respawned once it's eaten
class Food:
	def __init__(self):
		self.mesh = Mesh("meshes/food.mesh")
		self.scale = 1
		self.modelMatrix = scaleMatrix(self.scale)
		self.color = vec3(0.8, 0.1, 0.1)
		
		self.position = (2 * numpy.random.random(3) - 1) * 30
		self.rotation = 0

	def draw(self, shader):
		self.updatePosition()
		
		# Apply movement
		glUseProgram(shader)
		glUniformMatrix4fv(glGetUniformLocation(shader, "modelMatrix"), 1, GL_TRUE, self.modelMatrix)
		glUniform3fv(glGetUniformLocation(shader, "color"), 1, self.color)
		glUseProgram(0)
		
		self.mesh.draw(shader)

	def updatePosition(self):
		self.rotation += 0.1
		self.modelMatrix = translationMatrix(self.position) @ rotationMatrixY(self.rotation) @ scaleMatrix(self.scale)

# World outline class
class World:
	def __init__(self):
		self.mesh = Mesh("meshes/cube.mesh")
		self.scale = 60
		self.modelMatrix = scaleMatrix(self.scale) @ translationMatrix(vec3(-0.5, -0.5, -0.5))
		self.color = vec3(0.9, 0.9, 0.9)
	
	def draw(self, shader):
		glUseProgram(shader)
		glUniformMatrix4fv(glGetUniformLocation(shader, "modelMatrix"), 1, GL_TRUE, self.modelMatrix)
		glUniform3fv(glGetUniformLocation(shader, "color"), 1, self.color)
		glUseProgram(0)
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		self.mesh.draw(shader)
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		
		

# Game class
class Game:
	def __init__(self):
		self.context = GLContext()
		self.shader = self.context.createShader("shaders/simple.vert", "shaders/simple.frag")

		# Generate Game components
		# Camera
		self.cameraPosition = vec3(50,10,100)
		self.projectionMatrix = perspective(45.0, 1, 0.1, 1000.0)
		self.viewMatrix = lookAt(self.cameraPosition, self.cameraPosition + numpy.array([0,0,-1]), numpy.array([0,1,0]))
		self.modelMatrix = identityMat
		self.updateMatrices()

		# World
		self.world = World()

		# Bot
		self.bot = Bot()
		
		# Food
		self.food = Food()
		
		# Timing
		self.lastTime = glfw.get_time()

	def updateMatrices(self):
		glUseProgram(self.shader)
		glUniformMatrix4fv(glGetUniformLocation(self.shader, "projectionMatrix"), 1, GL_TRUE, self.projectionMatrix)
		glUniformMatrix4fv(glGetUniformLocation(self.shader, "viewMatrix"), 1, GL_TRUE, self.viewMatrix)
		glUniformMatrix4fv(glGetUniformLocation(self.shader, "modelMatrix"), 1, GL_TRUE, self.modelMatrix)
		glUseProgram(0)

	def loop(self):
		while not glfw.window_should_close(self.context.window):
			glClearColor(0.8, 0.8, 0.8, 1.0)
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
			
			currentTime = glfw.get_time()
			timeStep = currentTime - self.lastTime
			self.lastTime = currentTime
		
			# Move camera
			#self.cameraPosition = self.cameraPosition + numpy.array([0.01, 0, -0.01])
			self.viewMatrix = lookAt(self.cameraPosition, vec3(0,0,0), vec3(0,1,0))
			self.updateMatrices()
			
			# Draw world
			self.world.draw(self.shader)
			
			# Draw bot
			direction = self.food.position - self.bot.position
			self.bot.calcPhysics(timeStep, direction)
			self.bot.draw(self.shader)
			
			# Draw food
			if numpy.linalg.norm(direction) < 3:
				self.food.position = (2 * numpy.random.random(3) - 1) * 30
			self.food.draw(self.shader)
			
			glfw.swap_buffers(self.context.window)
			glfw.poll_events()
		glfw.terminate()








