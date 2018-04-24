#version 330 core

in vec4 fragPosition;

out vec4 fragColor;

uniform vec3 color;

void main(void)
{
	fragColor = vec4(0.0, (1.0 - fragPosition.z)/2, fragPosition.z/2, 1.0);
	fragColor = vec4(color, 1.0);
	//fragColor = fragPosition;
}
