<?php
function get_video_id() {
	// Read video_data.json file
	$file_contents = file_get_contents('video_data.json');

	if ($file_contents === false) {
		return null; // Return null if file cannot be read
	}

	$data = json_decode($file_contents, true);

	if (isset($data['video_id'])) {
		return $data['video_id'];
	} else {
		return null;
	}
}

$video_id = get_video_id();
?><!doctype html>
<html lang="de">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-M1V279GYJR"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-M1V279GYJR');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;1,400&family=Neucha&display=swap" rel="stylesheet">
    <link href="style.css" rel="stylesheet">

    <!-- Primary Meta Tags -->
    <title>Bird Box Basel - Der Nistkasten mit Livestream</title>
    <meta name="title" content="Bird Box Basel - Der Nistkasten mit Livestream" />
    <meta name="description" content="Bei uns nisten Kohlmeisen. Schau ihnen live zu, wie sie ihr Nest bauen und ihre Jungen aufziehen." />

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://birdboxbasel.pm7.ch/" />
    <meta property="og:title" content="Bird Box Basel - Der Nistkasten mit Livestream" />
    <meta property="og:description" content="Bei uns nisten Kohlmeisen. Schau ihnen live zu, wie sie ihr Nest bauen und ihre Jungen aufziehen." />
    <meta property="og:image" content="/img/share-image.jpg" />

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:url" content="https://birdboxbasel.pm7.ch/" />
    <meta property="twitter:title" content="Bird Box Basel - Der Nistkasten mit Livestream" />
    <meta property="twitter:description" content="Bei uns nisten Kohlmeisen. Schau ihnen live zu, wie sie ihr Nest bauen und ihre Jungen aufziehen." />
    <meta property="twitter:image" content="/img/share-image.jpg" />

    <link rel="apple-touch-icon" sizes="180x180" href="/img/icons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/img/icons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="194x194" href="/img/icons/favicon-194x194.png">
    <link rel="icon" type="image/png" sizes="192x192" href="/img/icons/android-chrome-192x192.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/img/icons/favicon-16x16.png">
    <link rel="manifest" href="/img/icons/site.webmanifest">
    <link rel="mask-icon" href="/img/icons/safari-pinned-tab.svg" color="#d9ba6a">
    <link rel="shortcut icon" href="/img/icons/favicon.ico">
    <meta name="msapplication-TileColor" content="#f8ebd8">
    <meta name="msapplication-config" content="/img/icons/browserconfig.xml">
    <meta name="theme-color" content="#f8ebd8">
</head>
<body class="bg-beige">
<header>
    <div class="container flex">
        <div class="element">
            <img src="./img/profile-200.jpg" alt="Profile picture" class="profile-picture">
        </div>
        <div class="element">
            <h1 class="page-title">Bird Box Basel</h1>
            <p><i>Bei uns nisten Kohlmeisen. Schau ihnen live zu, wie sie ihr Nest bauen und ihre Jungen aufziehen. <br>Auf Youtube abonnieren: <a href="https://www.youtube.com/@birdboxbasel">https://www.youtube.com/@birdboxbasel</a></i></p>
        </div>
    </div>
</header>

<div class="container flex space-between align-flex-end">
    <h2>Livestream</h2>
    <p>Status: <img src="https://healthchecks.io/badge/0f023cd7-2051-4442-aa81-9768e3/NnMrajpw-2.svg" alt="Livestream Status"></p>
</div>

<div class="container">
    <div class="youtube-video-container">
        <iframe src="https://www.youtube.com/embed/<?php echo $video_id ?>" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    </div>
</div>

<div class="container">
    <h2>Highlights & Zusammenschnitte</h2>
    <div class="youtube-video-container">
        <iframe src="https://www.youtube.com/embed/videoseries?si=I49rRJCcGa703ldJ&amp;list=PLu7ESxuA5rqYwSoguHEcJWGNJhWYFn5gr" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    </div>
</div>

<div class="container flex">
    <h2>Der Nistkasten</h2>
</div>

<div class="container flex photo-50">
    <figure>
        <img src="./img/vogelhaus_1_800.jpg" alt="Nistkasten von vorne">
        <figcaption>Der Nistkasten von vorne. Oben unter der Schicht Silikon ist die Kamera verbaut.</figcaption>
    </figure>
    <figure>
        <img src="./img/vogelhaus_2_800.jpg" alt="Nistkasten von oben">
        <figcaption>Der Nistkasten von oben. Oben die Kamera, auf der rechten Seite eine wasserdichte Box mit einem Raspberry Pi.</figcaption>
    </figure>
</div>

<footer>
    <div class="container flex">
        <div class="element">
            <p><b>Youtube:</b></p>
            <script src="https://apis.google.com/js/platform.js"></script>

            <div class="g-ytsubscribe" data-channelid="UC5Xn3H8I6R_gYSkMfq4rpnA" data-layout="full" data-count="hidden"></div>
        </div>

        <div class="element">
            <p><b>Kontakt:</b></p>
            <p><a href="mailto:birdboxbasel@pm7.ch">birdboxbasel@pm7.ch</a></p>
        </div>
    </div>
</footer>
</body>
</html>