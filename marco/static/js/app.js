$('.btn-add-container').click(function() {
  var self = $(this),
      url = self.data('url'),
      host = '5';
  $.post(url, {host_id: host}).fail(function (e){
    alert('出错了');
  }).done(function(r) {
    if (!r.r) {
      alert('添加成功, 稍等');
      window.location.reload();
    } else {
      alert('有什么错');
    }
  });
});


$('.btn-remove-container').click(function() {
  var self = $(this),
      url = self.data('url'),
      host = '5';
  $.post(url, {host_id: host}).fail(function (e){
    alert('出错了');
  }).done(function(r) {
    if (!r.r) {
      alert('下线成功, 稍等');
      window.location.reload();
    } else {
      alert('有什么错');
    }
  });
});
