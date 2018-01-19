/* pyLib.cpp
 * 
 * See also:
 *     http://www.boost.org/doc/libs/1_63_0/libs/python/doc/html/index.html
 *     http://www.boost.org/doc/libs/1_63_0/libs/python/doc/html/article.html
 */
#include <boost/python.hpp>
#include <boost/numpy.hpp>

namespace BP = boost::python ;
namespace BN = boost::numpy ;

// Direct copy of the fragment from:
//     https://stackoverflow.com/questions/10701514/how-to-return-numpy-array-from-boostpython

std::vector<double> myfunc(){
    std::vector<double> numbers ;
    numbers.pushback( 1.0 ) ;
    numbers.pushback( 2.0 ) ;
    numbers.pushback( 3.0 ) ;
    numbers.pushback( 4.0 ) ;
    numbers.pushback( 5.0 ) ;
    numbers.pushback( 6.0 ) ;
    numbers.pushback( 7.0 ) ;
    numbers.pushback( 8.0 ) ;
    return numbers ;
}

bn::ndarray mywrapper() {
    std::vector<double> v = myfunc() ;
    Py_intptr_t shape[1] = { v.size() } ;
    BN::ndarray result = BN::zeros( 1, shape, BN::dtype::get_builtin<double>() ) ;
    std::copy( v.begin(), v.end(), reinterpret_cast<double*>( result.get_data() ) ) ;
    return result ;
}

BOOST_PYTHON_MODULE( example ) {
    BN::initialize() ;
    
    BP::def( "myfunc", mywrapper ) ;
}

// Variable arguments ? https://www.tutorialspoint.com/cprogramming/c_variable_arguments.htm
// Note: http://www.skotheim.net/wiki/Boost_Python

// My Idea for an NP ndarray Template function
template<class T>
BN::ndarray ndarray1ax( const int32_t len ) {
    return BN::zeros( BP::make_tuple( len ), BN::dtype::get_builtin< T >() ) ;
} // make ndarray with 1 axis

template<class T>
BN::ndarray ndarray2ax( const int32_t rows, const int32_t cols ) {
    return BN::zeros( BP::make_tuple( rows, cols ), BN::dtype::get_builtin< T >() ) ;
} // make ndarray with 2 axis

template<class T>
BN::ndarray ndarray3ax( const int32_t rows, const int32_t cols, const int32_t dims ) {
    return BN::zeros( BP::make_tuple( rows, cols, dims ), BN::dtype::get_builtin< T >() ) ;
} // make ndarray with 3 axis

// but no one is talking about refcount!!