import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders

class GLContext:
	window = None

	def __init__(self):
		if not glfw.init():
			return
	
		glfw.window_hint(glfw.SAMPLES, 4);
		glfw.window_hint(glfw.RESIZABLE, GL_FALSE);
		glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3);
		glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3);
		glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE);

		self.window = glfw.create_window(600, 600, "3DSnake", None, None)

		if not self.window:
			glfw.terminate()
			return

		glfw.make_context_current(self.window)
		
		# OpenGL settings
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LESS)

	def createShader(self, vsFilename, fsFilename):
		with open(vsFilename, 'r') as vsFile:
			vsString = vsFile.read()

		vs = OpenGL.GL.shaders.compileShader(vsString, GL_VERTEX_SHADER)
		
		with open(fsFilename, 'r') as fsFile:
			fsString = fsFile.read()
		fs = OpenGL.GL.shaders.compileShader(fsString, GL_FRAGMENT_SHADER)

		sp = OpenGL.GL.shaders.compileProgram(vs, fs)
		return sp


