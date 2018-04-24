#version 330 core

layout (location = 0) in vec3 inPosition;

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;

out vec4 fragPosition;

void main()
{
	mat4 mvp = projectionMatrix * viewMatrix * modelMatrix;
	fragPosition = modelMatrix * vec4(inPosition, 1.0);
	gl_Position = mvp * vec4(inPosition, 1.0);
}
