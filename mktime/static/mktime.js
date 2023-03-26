$(".jumbotron").css({ height: $(window).height() * 0.93 + "px" });

$(window).on("resize", function () {
	$(".jumbotron").css({ height: $(window).height() * 0.93 + "px" });
});

// wanted 93% of screen to accomodate navbar and to bring footer closer
