$('.btn-create-app').click(function() {
  var name = $('input[name=name]').val(),
      runtime = $('select[name=runtime]').val(),
      ns = $('select[name=namespace]').val();
  var errdis = $('.error-display');
  $.post('/manage/create', 
    {name: name, runtime: runtime, namespace: ns}
  ).fail(function() {
    errdis.html('<div class="alert alert-danger">出错了</div>');
  }).done(function(r) {
    if (!r.r) {
      errdis.html('<div class="alert alert-info">创建成功</div>');
      $('.close').trigger('click');
    } else {
      errdis.html('<div class="alert alert-danger">'+r.error+'<div>');
    }
  });
})

$('.btn-import-app').click(function() {
  var addr = $('input[name=addr]').val(),
      runtime = $('select[name=runtime]').val(),
      y = $('input[name=appyaml]:checked').length;
  var errdis = $('.error-display');
  $.post('/manage/import', 
    {addr: addr, runtime: runtime, appyaml: y}
  ).fail(function() {
    errdis.html('<div class="alert alert-danger">出错了</div>');
  }).done(function(r) {
    if (!r.r) {
      errdis.html('<div class="alert alert-info">创建成功</div>');
      $('.close').trigger('click');
    } else {
      errdis.html('<div class="alert alert-danger">'+r.error+'<div>');
    }
  });
})
