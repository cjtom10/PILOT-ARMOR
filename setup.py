from setuptools import setup

setup(
    name='PILOT ARMOR',
    options={
        'build_apps': {
            # Build asteroids.exe as a GUI application
            'gui_apps': {
                'PILOT ARMOR': 'src/main.py',
            },

            # Specify which files are included with the distribution
            'include_patterns': [
                '**/*.png',
                '**/*.glb',
                '**/*.blend',
                '**/*.blend1',
                '**/*.bam',
                '**/*.egg',
                '**/*.ai',
            ],

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
        }
    }
)
