// - For sanity
#![allow(non_snake_case)]
#![allow(non_camel_case_types)]
#![allow(unused_imports)]


// - Externs
extern crate num ;
use num::Complex ;

extern crate image ;
use image::ColorType ;
use image::png::PngEncoder ;


// - Imports
use std::str::FromStr ;
use std::fs::File ;
use std::io::Write ;


fn escapeTime( c: Complex<f64>, its: u32 ) -> Option<u32> {
	let mut z = Complex { re: 0.0, im: 0.0 } ;
	for i in 0..its {
		z = z*z + c ;
		if z.norm_sqr() > 4.0 {
			return Some( i ) ;
		}
	}
	// Doesn't escape
	None
}

fn parsePair<T: FromStr>( in_str: &str, sep: char ) -> Option<(T, T)> {
	match in_str.find( sep ) {
		None => {
			None
		}
		Some( index ) => {
			// Sep found, cast both sides
			match( T::from_str( &in_str[..index] ), T::from_str( &in_str[index + 1..]) ) {
				( Ok(l), Ok(r) ) => {
					Some( (l, r) )
				}
				_ => {
					None
				}
			} // match sides
		}
	} // has sep?
}

#[test]
fn test_parsePair() {
	assert_eq!( parsePair::<i32>("", ','), None ) ;
	assert_eq!( parsePair::<i32>("10,", ','), None ) ;
	assert_eq!( parsePair::<i32>(",10", ','), None ) ;
	assert_eq!( parsePair::<i32>("10,20", ','), Some((10, 20)) ) ;
	assert_eq!( parsePair::<i32>("10,20xy", ','), None ) ;
	assert_eq!( parsePair::<f64>("0.5x", 'x'), None ) ;
	assert_eq!( parsePair::<f64>("0.5x1.5", 'x'), Some((0.5, 1.5)) ) ;
}

fn parseComplex( in_str: &str ) -> Option<Complex<f64>> {
	match parsePair( in_str, ',' ) {
		Some( (re, im)) => {
			Some( Complex { re, im } )
		}
		None => {
			None
		}
	}
}

#[test]
fn test_parseComplex() {
	assert_eq!(parseComplex("1.25,-0.0625"), Some(Complex { re: 1.25, im: -0.0625 }));
	assert_eq!(parseComplex(",-0.0625"), None);
}

fn pix2Point(
	bounds: (usize, usize),
	pixel: (usize, usize),
	up_left: Complex<f64>,
	lo_right: Complex<f64> )
-> Complex<f64>
{
	let (w, h) = (lo_right.re - up_left.re, up_left.im - lo_right.im ) ;
	Complex {
		re: up_left.re + pixel.0 as f64 * w / bounds.0 as f64,
		im: up_left.im - pixel.1 as f64 * h / bounds.1 as f64
	}
}

#[test]
fn test_pixel_to_point() {
	assert_eq!( pix2Point(
		(100, 100),
		(25, 75),
		Complex { re: -1.0, im: 1.0 },
		Complex { re: 1.0, im: -1.0 }),
	// res
		Complex { re: -0.5, im: -0.5 }
	);
}

fn renderBrot(
	pixels: &mut[u8],
	bounds: (usize, usize),
	up_left: Complex<f64>,
	lo_right: Complex<f64>)
{
	assert!(pixels.len() == (bounds.0 * bounds.1) ) ;

	for row in 0..bounds.1 {
		for col in 0..bounds.0 {
			let point = pix2Point( bounds, (col, row), up_left, lo_right ) ;
			pixels[ (row*bounds.0) + col ] = 
				match escapeTime( point, 255 ) {
					Some( count ) => {
						255 - count as u8 
					}
					None => {
						0
					}
				} ;
		} // c
	}// r
}

fn writeImg(
	filename: &str,
	pixels: &[u8],
	bounds: (usize, usize) )
-> Result<(), std::io::Error>
{
	let output = File::create( filename )? ;
	let encoder = PngEncoder::new( output ) ;

	encoder.encode( &pixels, bounds.0 as u32, bounds.1 as u32, ColorType::L8 ).expect("!!!") ;


	Ok(())
}


fn main() {
    let args: Vec<String> = std::env::args().collect() ;

	if args.len() != 5 {
		writeln!(std::io::stderr(), "Usage: mandelbrot FILE PIXELS UPPERLEFT LOWERRIGHT")
			.unwrap();

		writeln!(std::io::stderr(), "Example: {} mandel.png 1000x750 -1.20,0.35 -1,0.20", args[0])
			.unwrap();

		std::process::exit(1);
	} // arg sanity

	let bounds   = parsePair( &args[2], 'x' ).expect( "error parsing image dimensions" ) ;
	let up_left  = parseComplex( &args[3] ).expect( "error parsing upper left corner point" ) ;
	let lo_right = parseComplex( &args[4] ).expect( "error parsing lower right corner point" ) ;

	let mut pixels = vec![0; bounds.0 * bounds.1] ;

	renderBrot( &mut pixels, bounds, up_left, lo_right ) ;

	writeImg( &args[1], &pixels, bounds ).expect( "error writing PNG file" ) ;
}
