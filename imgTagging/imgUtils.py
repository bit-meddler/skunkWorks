""" Image Utilities """
import os

def fragmentFilePath( file_fq ) :
    """ returns path, name, and extension of an FQ path """
    path_name, ext = os.path.splitext( file_fq )
    path_part = os.path.dirname( path_name )
    name_part = os.path.basename( path_name )
    return path_part, name_part, ext
    
    
class ImageTester( object ):

    KNOWN_4CC = {
        b'GIF89a'                   : ".gif",
        b'\x89PNG\r\n'              : ".png",
        b'\xff\xd8\xff\xe0\x00\x10' : ".jpg",
    }
    
    def __init__( self ):
        self.reset()
        
    def reset( self ):
        self.ext = ""
        self.img_type = ""
        self.is_anim = False
        self.fh = None
        
    def test( self, file_fq ):
        self.reset()
        file_path, file_name, file_ext = fragmentFilePath( file_fq )
        self.ext = file_ext
        self.fh = open( file_fq, "rb" )
        # Do tests
        self._test4CC()
        if( self.img_type == ".gif" ):
            self._testGifAnim()
        # Tidy Up
        self.fh.close()
        
    def _test4CC( self ):
        self.fh.seek( 0 )
        four_cc = self.fh.read( 6 )
        if( four_cc in self.KNOWN_4CC ):
            self.img_type = self.KNOWN_4CC[ four_cc ]
        else:
            print( "Unknown 4CC code '{}' in '{}' file.".format( four_cc, self.ext ) )
            
    # - Gif testing internals - This may have come from stackoverflow... I Don't recall TBH
    
    def __skipColorTable( self, packed_byte ):
        """this will fh.seek() completely past the color table"""
        has_gct = (packed_byte & 0b10000000) >> 7
        gct_size = packed_byte & 0b00000111

        if has_gct:
            global_color_table = self.fh.read( 3 * pow( 2, (gct_size + 1) ) )

    def __skipImageData( self ):
        """skips the image data, which is basically just a series of sub blocks
        with the addition of the lzw minimum code to decompress the file data"""
        lzw_minimum_code_size = self.fh.read( 1 )
        self.__skipSubBlocks()

    def __skipSubBlocks( self ):
        """skips over the sub blocks

        the first byte of the sub block tells you how big that sub block is, then
        you read those, then read the next byte, which will tell you how big
        the next sub block is, you keep doing this until you get a sub block
        size of zero"""
        num_sub_blocks = ord( self.fh.read( 1 ) )
        while( num_sub_blocks != 0x00 ):
            self.fh.read( num_sub_blocks )
            num_sub_blocks = ord( self.fh.read( 1 ) )
            
    # - Gif Internals
    
    def _testGifAnim( self ):
        self.fh.seek( 0 )
        ret = False
        image_count = 0
        
        header = self.fh.read(6)
        
        if( header != b"GIF89a" ): # GIF87a doesn't support animation
            self.is_anim = False
            return
            
        logical_screen_descriptor = self.fh.read( 7 )
        self.__skipColorTable( logical_screen_descriptor[4] )

        key = ord( self.fh.read( 1 ) )
        while( key != 0x3B ): # 3B is always the last byte in the gif
            if( key == 0x21 ): # 21 is the extension block byte
                key = ord( self.fh.read( 1 ) )
                if( key == 0xF9 ): # graphic control extension
                    block_size = ord( self.fh.read( 1 ) )
                    self.fh.read( block_size )
                    key = ord( self.fh.read( 1 ) )
                    if( key != 0x00 ):
                        raise ValueError("GCT should end with 0x00")

                elif( key == 0xFF ): # application extension
                    block_size = ord( self.fh.read(1) )
                    self.fh.read(block_size)
                    self.__skipSubBlocks()

                elif( key == 0x01 ): # plain text extension
                    block_size = ord( fp.read( 1 ) )
                    self.fh.read( block_size )
                    self.__skipSubBlocks()

                elif( key == 0xFE ): # comment extension
                    self.__skipSubBlocks()

            elif( key == 0x2C ): # Image descriptor
                # if we've seen more than one image it's animated
                image_count += 1
                if( image_count > 1 ):
                    ret = True
                    break

                # total size is 10 bytes, we already have the first byte so
                # let's grab the other 9 bytes
                image_descriptor = self.fh.read( 9 )
                self.__skipColorTable( image_descriptor[-1] )
                self.__skipImageData()

            key = ord( self.fh.read( 1 ) )

        self.is_anim = ret
    
    
    def report( self ):
        return self.ext, self.img_type, self.is_anim
    
# Testing
if( __name__ == "__main__" ):
    test_imgs_path = r"C:\temp\testImgs"
    tester = ImageTester()

    for _, _, files in os.walk( test_imgs_path ):
        for name in files:
            file_fq = os.path.join( test_imgs_path, name )
            tester.test( file_fq )
            print( name, tester.report() )










      
