<?php

function respondWithJson( $data, $status_code = 200 ) {
	http_response_code( $status_code );
	header( 'Content-Type: application/json' );
	echo json_encode( $data );
	exit;
}

// Check if the request method is POST
if ( $_SERVER['REQUEST_METHOD'] === 'POST' ) {
	// Check if the secret is provided and correct
	$providedSecret = $_POST['secret'];
	$expectedSecret = '';
	if ( $providedSecret !== $expectedSecret ) {
		respondWithJson( array( 'error' => 'Authentication failed' ) . 401 );
	}

	// Check if video_url parameter is provided
	if ( ! isset( $_POST['video_id'] ) ) {
		respondWithJson( array( 'error' => 'Parameter video_id is missing' ), 400 );
	}

	// Get video_url parameter
	$videoId = htmlspecialchars($_POST['video_id']);

	// Save video_url to JSON file
	$data = array( 'video_id' => $videoId,  );
	file_put_contents( 'video_data.json', json_encode( $data ) );

	respondWithJson( array( 'message' => 'Video URL updated successfully' ), 200 );
} else {
	respondWithJson( array( 'error' => 'Not a valid request' ), 405 );
}
