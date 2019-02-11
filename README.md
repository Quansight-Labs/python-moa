# Mathematics of Arrays (MOA)

# Philosophy

This is a proof of concept with some assertions.

1. Assumes that shapes can be fuly calculatted (soon only dimension)
2. All code is written with the idea that it will be ported to a low
   level language. Therefore skip constructs that don't have
   equivalent implmentations. One major exception is that it is
   acceptable if it is straighforard to replace and makes the code
   clearer and easier to debug.
    - examples: enum int -> str, dict -> arrays
3. Code should be simple and have zero dependencies except for
   testing.
4. This code is meant as an exploration
