$(document).ready(function() {
  $('.album').each(function() {
    var dl = $('<span class="ipodDl">↡</span>');

    dl.click(function() {
      $.post('ipod', {album: $(this).parent().attr('about') });
    });

    $(this).prepend(dl);
  });
});
