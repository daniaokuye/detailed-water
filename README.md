# detailed-water
### aims:   
remove adjacent effect and mixing pixels effect for inland water bodies  
### main factor involved in the algorithm  
adjacent effect & mixed pixels effect  
### the importance of detailed water  
Quantitative analysis in not alway can be satisfied in remote sensing. For some objects, the normal situation is a phenomenon that same object with different spectra  
### which data of remote sensing is the study one  
any spatial resolution is suppoed full of detailed water. but we perfer to MODIS in this paper


# How to use this algorithm  
1. we suppose you can run a python code in local machine.
2. the main function is "Main.py"
3. you can fill according bands in the blank and run it  


# TODO
1. I want to add more explanation in code further. It will be easier to understand if read my corresponding paper.
2. A chart flow may help to better understand it. we will add such one in the future.



# FAQ
* the defination of detailed water   
    
    At first, we suppose it is a concepts about spatial resolution. Maybe it is very hard to extract from image by general method.  
    Then, these part water has certain carrier of information, such as slender river or boundary of open water. It's better to distinguish between detailed water and slender river etc.
    At last, if we check papers in history, we can find out this question make researches suck in trouble for a long time. For example, Paul Shane Frazier (2000), Lu et.al (2011) and Sarp and Ozcelik (2016) are all reference the question.
    To sum up, we want to figure out such a question: "whether or not can a algorithm extract water bodies which can be distinguished by professor but with a phenomenon that same object with different spectra".
    
* whether monitering the dynamic change of real water included in detailed water
    no, we perfer to find solution to extract water in static status.

* Is proposed algorithm functioned in a total automatic way
    yes, it is. 1. it can located mixed pixels in image without supervised threhold or anything else. 2. the method can find local suitable endmembers adaptively.
    
* Does the method involves ways to deal with dark objects, such as shadows.
    The shadow in remote sensing is a hard question, too. Many method has been proposed as far, such as water indexes. We incline to find solution towards detailed water in this paper which is seldom be focused. Shadow is neither the main factor leading to detailed water nor exist in image generally. Therefoe, we employ water index to suppress non-water noise here.
    
