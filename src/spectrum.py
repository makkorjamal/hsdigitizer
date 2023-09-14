class Spectrum:

    # This class saves the spectrum data 
    def __init__(self,img_name,img_shape, sp_name, calsp_name = None, calsplines_name  = None, sp_range = []):
        
        #If an attribute is added here it shoud be updated in the jsonparser class
        self.img_name= img_name 
        self.img_shape= img_shape
        self.sp_name = sp_name
        self.sp_range = sp_range
        self.calsp_name = calsp_name
        self.calsplines_name = calsplines_name
    

