function saveRating() {
  var star = $(this);
  var value = star.prevAll().length + 1;
  var album = $(this).parent().parent();
  var uri = album.attr('about');

  $.post('rate', {uri: uri, rating: value}, function(data) {
    star.prevAll().text('★').addClass('selected');
    star.parent().attr('content', value);
  }, 'text');
}

$(document).ready(function() {
  $('.score .star').hover(function() {
    /* black stars */
    $(this).prevAll().text('★').addClass('selected');
    $(this).text('★').addClass('selected');
    $(this).nextAll().text('☆').removeClass('selected');
  }, function() {
    /* white stars */
    var scoreSpan = $(this).parent();
    var r = parseInt(scoreSpan.attr('content'));
    scoreSpan.children('.star').slice(0, r).text('★').addClass('selected');
    scoreSpan.children('.star').slice(r).text('☆').removeClass('selected');
  });

  $('.score .star').click(saveRating);
});
