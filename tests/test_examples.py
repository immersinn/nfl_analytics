
import types
import unittest

class TestAccess( unittest.TestCase ):
    def test_should_add_and_get_attribute( self ):
        self.object.new_attribute = True
        self.assertTrue( self.object.new_attribute )
    def test_should_fail_on_missing( self ):
        self.assertRaises( AttributeError, lambda: self.object.undefined )


class SomeClass:
    pass


class Test_EmptyClass( TestAccess ):
    def setUp( self ):
        self.object = SomeClass()

        
class Test_Namespace( TestAccess ):
    def setUp( self ):
        self.object = types.SimpleNamespace()


class Test_Object( TestAccess ):
    def setUp( self ):
        self.object = object()


def suite():
    s = unittest.TestSuite()
    s.addTests ( unittest.defaultTestLoader.loadTestsFromTestCase(Test_EmptyClass) )
    s.addTests ( unittest.defaultTestLoader.loadTestsFromTestCase(Test_Namespace) )
    s.addTests ( unittest.defaultTestLoader.loadTestsFromTestCase(Test_Object) )
    return(s)

if __name__ == "__main__":
    t = unittest.TextTestRunner()
    t.run( suite() )
