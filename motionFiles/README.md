# Motion File Parsers

A few experiments and some sample data for developing I/O filters for common motion files.

Also interesting to see the differences between files generated in Motionbuilder Vs Blade.  It would be great to get a Giant derived ASF/AMC pair to see how Mobu and Vicon differ to an origenal file.

## HTR
MAC Native skeleton type.  Joint tree, followed by channel data

## TRC
MAC Native 3D positional data

## BVH
Biovision Format - not bad actually

## C3D
Andrew Danis? File format.  Actually really bad, but for some reason an improvement has appeard

## ASF/AMC
Acclaim / Giant / LEI interchange format.  Not the _Internal_ format of MDL/DOF/BDF and BMO.  Actually pretty nasty because it works in a bone system, so many dummey joints are created to attach children to.

## Skeleton Maths
I may end up with a maths library for dealing with common skeleton problems
