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

$('.btn-build-image').click(function() {
  var self = $(this),
    url = self.data('url'),
    base = $('#build-base').val(),
    host = '5';
  $.post(url, {host_id: host, base: base}).fail(function (e){
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

$('.btn-test-app').click(function() {
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

function getCheckList() {
  var r = [];
  $('.check-container').each(function(i, e) {
    if (e.checked) {
      r.push($(e).data('cid'));
    }
  });
  return r;
}

$('.container-list .check-container').click(function() {
  var cids = getCheckList();
  if (cids.length) {
    $('.btn-remove-containers').removeClass('disabled');
  } else {
    $('.btn-remove-containers').addClass('disabled');
  }
});

$('.btn-collect-all').click(function() {
  var self = $(this),
    cs = $('.check-container'),
    checkCs = getCheckList();
  if (checkCs.length != cs.length) {
    cs.each(function(i, e) {
      e.checked = true;
    });
    $('.btn-remove-containers').removeClass('disabled');
    self.html('取消全选');
  } else {
    cs.each(function(i, e) {
      e.checked = false;
    });
    $('.btn-remove-containers').addClass('disabled');
    self.html('选择全部');
  }
});

$('.btn-remove-containers').click(function() {
  var self = $(this),
      url = self.data('url'),
      cids = getCheckList();
  if (cids.length) {
    if (!confirm('确定要删除这些容器么')) {
      return;
    }
    $.post(url, {cids: cids}).fail(function(e) {
      alert('删除失败');
    }).done(function(r) {
      if (!r.r) {
        alert('删除成功');
        $('.check-container').each(function(i, e) {
          if (e.checked) {
            $(e).parent().parent().remove();
          }
        });
      } else {
        // ignore
      }
    });
  } else {
    alert("没有选择容器!");
  }
});

$('.btn-sync-db').click(function() {
  var self = $(this),
      url = self.data('url');
  $.post(url);
});

$('.btn-update-app').click(function() {
  var self = $(this),
      url = self.data('url'),
      version = self.data('version');
  $.post(url, {to_version: version}, function(d) {
    alert('更新成功, 坐等.');
  });
});
