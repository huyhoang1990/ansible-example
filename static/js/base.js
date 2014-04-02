var data = {
  pagespeed: [
    {
      label: 'http:\/\/ja-biz.demo.joomlart.com\/',
      data: [[88,1.2]]
    },
    {
      label: 'http:\/\/joomla-templates.joomlart.com\/ja_biz',
      data: [[78,0.2]]
    }],
  yslow: [
    {
      label: 'http:\/\/ja-biz.demo.joomlart.com\/',
      data: [[84,1.2]]
    },
    {
      label: 'http:\/\/joomla-templates.joomlart.com\/ja_biz',
      data: [[84,0.2]]
    }],
  pageload: [
    {
      label: 'http:\/\/ja-biz.demo.joomlart.com\/',
      data: [[2.128,1.2]]
    },
    {
      label: 'http:\/\/joomla-templates.joomlart.com\/ja_biz',
      data: [[5.474,0.2]]
    }],
  pagesize: [
    {
      label: 'http:\/\/ja-biz.demo.joomlart.com\/',
      data: [[915097,1.2]]
    },
    {
      label: 'http:\/\/joomla-templates.joomlart.com\/ja_biz',
      data: [[1636885,0.2]]
    }],
  requests: [
    {
      label: 'http:\/\/ja-biz.demo.joomlart.com\/',
      data: [[53,1.2]]
    },
    {
      label: 'http:\/\/joomla-templates.joomlart.com\/ja_biz',
      data: [[49,0.2]]
    }]
};

var graph_plotted = false;
function updateGraphs() {
  if (!graph_plotted) {
    try {
      var colors = [ '#8fc17b', '#7faad4', '#ecbd6a', '#e87e7e' ];
      var bars = { show: true, barWidth: .6, horizontal: true };
      var yaxis = { min: 0, max: 2, ticks: 0 };
      $.plot(
        $('#compare-pagespeed-graph'),
        data.pagespeed,
        {
          bars: bars,
          colors: colors,
          xaxis: {
            min: 0,
            max: 100,
            tickFormatter: function suffixFormatter(val, axis) {
              return val.toFixed(axis.tickDecimals) + '%';
            }
          },
          yaxis: yaxis,
          legend: { container: $('#compare-pagespeed-legend') }
        }
      );
      $.plot(
        $('#compare-yslow-graph'),
        data.yslow,
        {
          bars: bars,
          colors: colors,
          xaxis: {
            min: 0,
            max: 100,
            tickFormatter: function suffixFormatter(val, axis) {
              return val.toFixed(axis.tickDecimals) + '%';
            }
          },
          yaxis: yaxis,
          legend: { container: $('#compare-yslow-legend') }
        }
      );
      $.plot(
        $('#compare-pageload-graph'),
        data.pageload,
        {
          bars: bars,
          colors: colors,
          xaxis: {
            min: 0,
            tickDecimals: 1,
            tickFormatter: function suffixFormatter(val, axis) {
              return val.toFixed(axis.tickDecimals) + ' s';
            }
          },
          yaxis: yaxis,
          legend: { container: $('#compare-pageload-legend') }
        }
      );
      $.plot(
        $('#compare-pagesize-graph'),
        data.pagesize,
        {
          bars: bars,
          colors: colors,
          xaxis: {
            min: 0,
            tickFormatter: function suffixFormatter(val, axis) {
              if (val >= 1048576)
                return (val / 1048576).toFixed(axis.tickDecimals) + " MB";
              else if (val >= 1024)
                return (val / 1024).toFixed(axis.tickDecimals) + " KB";
              else
                return val.toFixed(axis.tickDecimals) + " B";
            }
          },
          yaxis: yaxis,
          legend: { container: $('#compare-pagesize-legend') }
        }
      );
      $.plot(
        $('#compare-requests-graph'),
        data.requests,
        {
          bars: bars,
          colors: colors,
          xaxis: { min: 0 },
          yaxis: yaxis,
          legend: { container: $('#compare-requests-legend') }
        }
      );
      graph_plotted = true;
    }
    catch (e) {
      graph_plotted = false;
    }
  }
}

$(document).ready(function() {
  updateGraphs();
  $('.tabs').data('tabs').onClick(function(clickEvent, index) {
    if (this.getPanes().get(index).id == 'report-graphs') {
      updateGraphs();
    }
  });

});