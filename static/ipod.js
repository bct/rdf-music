$(document).ready(function() {
  var ipodQueue = $('<ul id="ipodQueue"></ul>')

  $("body").append(ipodQueue);

  $('.album').each(function() {
    var dl = $('<span class="ipodDl">↡</span>');

    dl.click(function() {
      var album = $(this).parent();
      var li = $('<li>' + album.children('.title').text() + '</li>');
      ipodQueue.append(li);

      ipodQueue.queue(function() {
        var qi = $(this);

        $.post(app_path('ipod'), {album: album.attr('about') }, function() {
          li.remove();
          qi.dequeue();
        });
      });
    });

    $(this).prepend(dl);
  });
});
