// - For sanity
#![allow(non_snake_case)]
#![allow(non_camel_case_types)]
#![allow(unused_imports)]

// - Externs
extern crate iron ;
#[macro_use] extern crate mime ;

extern crate router ;
use router::Router ;

extern crate urlencoded;

// - Imports
use iron::prelude::* ;
use iron::status ;
use urlencoded::UrlEncodedBody;
use std::fmt ;
use std::str::FromStr;

const HOST: &str = "localhost" ;
const PORT: &str = "3003" ;

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

fn getForm( _request: &mut Request ) -> IronResult<Response> {
	let mut response = Response::new() ;
	response.set_mut( status::Ok ) ;
	response.set_mut( mime!( Text/Html; Charset=Utf8 ) ) ;
	response.set_mut( r#"<title>GCD Calculator</title>
<form action="/gcd" method="post">
<input type="text" name="n"/>
<input type="text" name="n"/>
<button type="submit">Compute GCD</button>
</form>"# ) ; // 2 'n's is deliberate

	Ok( response )
}

fn postGCD( request: &mut Request ) -> IronResult<Response> {
	let mut response = Response::new() ;

	// A good request?
	let form_data = match request.get_ref::<UrlEncodedBody>() {
		Ok( map ) => {
			// pass-thru return
			map
		}
		Err( e ) => {
			response.set_mut( status::BadRequest ) ;
			response.set_mut( format!("Error Parsing form data: {:?}\n", e) ) ;
			return Ok( response ) ;
		}
	} ;

	// test values
	let unparsed_numbers = match form_data.get("n") {
		Some( nums ) => {
			// pass-thru return
			nums
		}
		None => {
			response.set_mut( status::BadRequest ) ;
			response.set_mut( format!( "Missing n params" ) ) ;
			return Ok( response ) ;
		}
	} ;

	// Parse 'n's
	let mut numbers = Vec::new();
	for unparsed in unparsed_numbers {
		match u64::from_str( &unparsed ) {
			Ok( n ) => {
				numbers.push( n ) ;
			}
			Err( _e ) => {
				response.set_mut( status::BadRequest ) ;
				response.set_mut(
					format!( "Value for 'n' parameter not a number: {:?}\n", unparsed )
				) ;
				return Ok( response ) ;
			}
		} ;
	}

	let mut d = numbers[0];
	for m in &numbers[1..] {
		d = commonDenom( d, *m ) ;
	}

	response.set_mut( status::Ok ) ;
	response.set_mut( mime!(Text/Html; Charset=Utf8) ) ;
	response.set_mut(
		format!( "The greatest common divisor of the numbers {:?} is <b>{}</b>\n",
				numbers, d
		)
	);

	Ok( response )
}

fn main() {
	let adder = format!( "{}:{}", HOST, PORT ) ;

	let mut router = Router::new() ;
	router.get( "/", getForm, "root") ;
	router.post( "/gcd", postGCD, "gcd" ) ;

    println!( "Starting Webserver on http://{}", adder ) ;
    Iron::new( router ).http( adder ).unwrap() ;
}