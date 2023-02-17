# North_Natives_Generator
A fast Python script that converts a C++ Natives HPP file to a Python file that can be used in North scripts.

# How To Use #

  [1] Download the latest version of North_Natives_Generator
  
  [2] Acquire a Natives.hpp file. by going to https://nativedb.dotindustries.dev/natives and clicking Generate Code
  
  [3] Ensure that the Natives.hpp file is placed inside the same directory that the script is in
  
  [4] Open a terminal and run {your_python_env_variable} natives_gen.py
  
  [5] Locate your natives.py file in the same directory
  
  [6] To use the natives, simply import it into your script.
  
  Example:
    
    import natives # name of the generated file
    
    print(natives.is_player_online())
