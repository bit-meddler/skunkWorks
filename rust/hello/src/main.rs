#![allow(non_snake_case)]
#![allow(non_camel_case_types)]

use std::io::Write ;
use std::str::FromStr ;

fn commonDenom( mut n: u64, mut m: u64 ) -> u64 {
	assert!( n!=0 && m!=0 ) ;
	while  m!=0  {
		if  m<n  { // swap
			let temp = m ;
			m = n ;
			n = temp ;
		}
		m = m % n ;
	}
	// return
	n
}

#[test]
fn test_commonDenom() {
	assert_eq!( commonDenom( 14, 15 ), 1 ) ;
	assert_eq!( commonDenom( 2*3*5*11*17, 3*7*11*13*19 ), 3*11 ) ;
}

fn main() {
    let mut numbers = Vec::new() ;
    for arg in std::env::args().skip( 1 ) {
    	numbers.push( u64::from_str(&arg)
    				.expect("Error Passing") );
    }

    if  numbers.len() == 0  {
    	writeln!( std::io::stderr(), "give me some numbers" ).unwrap() ;
    	std::process::exit( 6 ) ;
    }

    let mut d = numbers[0] ;
    for m in &numbers[1..] {
    	d = commonDenom( d, *m ) ;
    }

    println!( "The divisor of {:?} is {}", numbers, d ) ;
}
