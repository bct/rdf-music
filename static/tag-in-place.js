$(document).ready(function(){
  $(".tags").each(function() {
    var editThing = $('<span class="inPlace">[t]</span>');
    var tags = $(this);
    editThing.click(function() {
      var uri = 'http://www.google.com/';

      var tagsInput = $("<input class='tagsInput' name='tags'>");
      tagsInput.attr('value', tags.text());

      tags.replaceWith(tagsInput);

      tagsInput.blur(function() {
        var wait = 'wait...';
        tagsInput.replaceWith(wait);
        $.post('./foo', {uri: uri, tags: tagsInput.attr('value')}, function(data) {
          wait.replaceWith('ok.');
        }, 'text');
      });

      tagsInput.focus();
    });
    tags.after(editThing);
  });
});
