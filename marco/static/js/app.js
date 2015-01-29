$('.btn-add-container').click(function() {
  var self = $(this),
      url = self.data('url'),
      daemon = $('#add-daemon').val(),
      subApp = $('#select-sub-app').val(),
      host = $('#add-host').val();
  $.post(url, {host_id: host, daemon: daemon, sub_app: subApp}).fail(function (e){
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
    host = $('#build-host').val();
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
    alert('坐等更新');
  });
});

$('.btn-add-mysql').click(function() {
  var self = $(this),
      url = self.data('url');
  $.post(url);
});

$('.btn-sub-apps').click(function() {
    $('#sub-apps-panel').overlay({
        title: '子应用设定'
    });
});

$('#sub-app-create').click(function() {
    if (! /^[a-zA-Z]+$/.test($('#sub-app-name').val())) {
        $('#sub-app-error').text('不合法的子应用名, 子应用名只能包含字母');
        return $('#sub-app-name').focus();
    }
    if (! /^[0-9]+$/.test($('#sub-app-port').val())) {
        $('#sub-app-error').text('不合法的端口号');
        return $('#sub-app-port').focus();
    }
    var port = parseInt($('#sub-app-port').val());
    if (!(1024 < port && port < 65536)) {
        $('#sub-app-error').text('端口号应该介于 1025 至 65535 之间');
        return $('#sub-app-port').focus();
    }
    $('#sub-app-error').text('');

    var self = $(this);
    $.post(['', 'app', self.data('name'), self.data('version'), 'addsub'].join('/'),
           $('#sub-apps-settings :input').toArray().reduce(function(obj, item) {
               if (item.name) {
                   obj[item.name] = item.value;
               }
               return obj;
           }, {}),
           function() {
               window.location.reload();
           });
});

$('.btn-sub-app-show').click(function() {
    var sub = $(this).data('sub');
    $('#sub-apps-settings :input').each(function() {
        if (!this.name) {
            return;
        }
        if (!sub[this.name]) {
            return $(this).val('');
        }
        if (typeof sub[this.name] !== 'object') {
            return $(this).val(sub[this.name]);
        }
        $(this).val(sub[this.name].join('\n'));
    });
    var subnames = sub.appname.split('-');
    $('#sub-app-name').val(subnames[subnames.length - 1]);
});
