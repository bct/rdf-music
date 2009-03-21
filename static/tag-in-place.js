function sendTags(event) {
  var wait = $('<span class="ajaxStatus">wait...</span>');

  var tagsInput = $(this);

  var sentTags = tagsInput.attr('value');
  if(sentTags == undefined)
    sentTags = '';

  tagsInput.replaceWith(wait);

  $.post(app_path('tag'), {uri: event.data.uri, tags: sentTags}, function(data) {
    event.data.tagsSpan.text(sentTags);
    wait.replaceWith(event.data.tagsSpan);
  }, 'text');
}

$(document).ready(function(){
  $(".tags").each(function() {
    var editThing = $('<span class="inPlace">[T]</span>');
    var tags = $(this);

    editThing.click(function() {
      var uri = tags.parent().attr('about');

      var tagsInput = $("<input class='tagsInput' name='tags'>");
      tagsInput.attr('value', jQuery.trim(tags.text()));

      tags.replaceWith(tagsInput);

      tagsInput.bind('blur', {uri: uri, tagsSpan: tags}, sendTags);

      tagsInput.focus();
    });

    tags.after(editThing);
  });
});
