function drawLineChart(data) {
  nv.addGraph(function() {
    var chart = nv.models.lineChart().height(400).width(800);
    chart.xAxis.axisLabel('时间')
      .tickFormat(function(d) {
        return d3.time.format('%X')(new Date(d));
    });
    chart.yAxis.axisLabel('CPU使用率').tickFormat(d3.format(',.5f'));
  
    d3.select('#chart')
        .datum(data)
        .transition()
        .attr('height', 400)
        .attr('width', 800)
        .call(chart);
  
    nv.utils.windowResize(chart.update);
  
    return chart;
  });
}

$(document).ready(function() {
  var s = $('#chart'),
      url = s.data('url');
  $.get(url, function(d) {
    drawLineChart(d.data);
  });
});
