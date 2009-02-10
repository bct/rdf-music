$(document).ready(function(){
  $(".tags").each(function() {
    var editThing = $('<span class="inPlace">[t]</span>');
    var tags = $(this);
    editThing.click(function() {
      var uri = tags.parent().attr('about');

      var tagsInput = $("<input class='tagsInput' name='tags'>");
      tagsInput.attr('value', tags.text());

      tags.replaceWith(tagsInput);

      tagsInput.blur(function() {
        var wait = $('<span class="ajaxStatus">wait...</span>');
        var sentTags = tagsInput.attr('value');
        tagsInput.replaceWith(wait);
        $.post('tag', {uri: uri, tags: sentTags}, function(data) {
          tags.text(sentTags);
          wait.replaceWith(tags);
        }, 'text');
      });

      tagsInput.focus();
    });
    tags.after(editThing);
  });
});
