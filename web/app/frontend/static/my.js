

// selections

var selected = ["home", null];
var s_e_date = [null, null];
var render_items = 25;

// elements

var body = $("body");
var menu = $("#menu");
var content = $("#content");

// data

var data_date = '';
var query_time = '';

var _company = {};
var _broker = {};

var _companies = [];
var _brokers = [];

// test data

var test_companies = [
    {code: "5465", name: "富華", open_price: 25.6, close_price: 26.7, focus: 0},
    {code: "5665", name: "富華", open_price: 25.6, close_price: 26.7, focus: 0},
    {code: "1802", name: "檯玻", open_price: 28, close_price: 26.7, focus: 1}
];

var test_brokers = [
    {code: "1A6f", name: "新光台中", focus: 1},
    {code: "1A62", name: "新光雞籠", focus: 0},
];

var red = "rgba(222, 47, 47, 0.8)";
var green = "rgba(15, 101, 15, 0.8)";

var test_company = {
    company: {
        code: '5465',
        name: '富華',
        focus: 1,
        data: [
            // date, open, high, low, close
            ['07-18', '23.65', '23.8', '23.6', '23.7'],
            ['07-19', '23.8', '24.45', '23.7', '24.05'],
            ['07-20', '24.15', '26.45', '24.15', '26.45'],
            ['07-21', '27.3', '29.05', '27.3', '29.05'],
            ['07-24', '29.25', '30', '28.4', '28.55'],
            ['07-25', '28.55', '29.2', '28.5', '29'],
            ['07-26', '29.1', '29.1', '28.4', '28.6'],
            ['07-27', '29.1', '29.35', '28.1', '28.3'],
            ['07-28', '28.9', '29', '27.05', '27.1']
        ],
        min_price: 22,
        max_price: 30,
        date: ['07-18', '07-19', '07-20', '07-21', '07-24', '07-25', '07-26', '07-27', '07-28'],
        amount: [197, 629, 1706, 7759, 3802, 2125, 891, 772, 1277],
        color: [red, red, red, red, green, red, green, green, green],
        percentage: [3,7,9,-10,5,3,8,2,5]
    },
    brokers: [
        {
            code: '1f8G',
            name: '富邦基隆',
            focus: 1,
            date: ['07-18', '07-19', '07-20', '07-21', '07-24', '07-25', '07-26', '07-27', '07-28'],
            buy_amount: [100, 200, 0, 300, 10, 79, 80, 11, 20],
            sell_amount: [15, 10, 80, 10, 0, 5, 350, 30, 15],
            all_amount: [115, 210, 80, 310, 10, 84, 480, 41, 35],
            acc_amount: [75, 265, 0, 485, 550, 635, 315, 296, 301],
            buy_amount_sum: 714,
            sell_amount_sum: 614,
            all_amount_sum: 1345,
            acc_amount_sum: 301
        },
    ]
};

var test_broker = {
    broker: {
        code: '1f8G',
        name: '富邦基隆',
        focus: 0,
    },
    companies: [
        {
            code: '5465',
            name: '富華',
            focus: 0,
            data: [
                // date, open, high, low, close
                ['07-18', '23.65', '23.8', '23.6', '23.7'],
                ['07-19', '23.8', '24.45', '23.7', '24.05'],
                ['07-20', '24.15', '26.45', '24.15', '26.45'],
                ['07-21', '27.3', '29.05', '27.3', '29.05'],
                ['07-24', '29.25', '30', '28.4', '28.55'],
                ['07-25', '28.55', '29.2', '28.5', '29'],
                ['07-26', '29.1', '29.1', '28.4', '28.6'],
                ['07-27', '29.1', '29.35', '28.1', '28.3'],
                ['07-28', '28.9', '29', '27.05', '27.1'],
            ],
            date: ['07-18', '07-19', '07-20', '07-21', '07-24', '07-25', '07-26', '07-27', '07-28'],
            amount: [197, 629, 1706, 7759, 3802, 2125, 891, 772, 1277],
            color: [red, red, red, red, green, red, green, green, green],
            percentage: [3,7,9,-10,5,3,8,2,5],
            buy_amount: [100, 200, 0, 300, 10, 79, 80, 11, 20],
            sell_amount: [15, 10, 80, 10, 0, 5, 350, 30, 15],
            all_amount: [115, 210, 80, 310, 10, 84, 480, 41, 35],
            acc_amount: [75, 265, 0, 485, 550, 635, 315, 296, 301],
            buy_amount_sum: 714,
            sell_amount_sum: 614,
            all_amount_sum: 1345,
            acc_amount_sum: 301
        },
    ]
};

// init

(function init () {

    setup();

    render_menu();

    ajax_api_1();

})();


// render

function render_menu () {
    // empty
    menu.empty();

    // menu - home
    let home = $('<div id="menu-home" class="menu-item">Home</div>');
    menu.append(home);

}

function render_content_home() {
    // empty
    content.empty();

    let waiting = $('<div class="waiting">Waiting...</div>');
    content.append(waiting);

    // 4 areas
    let content_home = $("<div id='content-home'></div>");
    let info_bar = $("<div class='info-bar'>DATE: " + data_date + ", QUERY: " + query_time + "</div>");
    let focus_companies = $("<div class='content-home-area'></div>");
    let focus_brokers = $("<div class='content-home-area'></div>");
    let unfocus_companies = $("<div class='content-home-area'></div>");
    let unfocus_brokers = $("<div class='content-home-area'></div>");

    _companies.map(function (company, i) {
        if (company.focus)
            if (company.close_price - company.open_price < 0) {
                let btn = $('<span id="' + company.code + '" class="company-button green-button">' +
                    company.code + company.name + ' ' + count_percentage(company.open_price, company.close_price) + '</span>');
                focus_companies.append(btn);
            }
            else {
                let btn = $('<span id="' + company.code + '" class="company-button red-button">' +
                    company.code + company.name + ' ' + count_percentage(company.open_price, company.close_price) + '</span>');
                focus_companies.append(btn);

            }
        else
            if (company.close_price - company.open_price < 0) {
                let btn = $('<span id="' + company.code + '" class="company-button green-button">' +
                    company.code + company.name + ' ' + count_percentage(company.open_price, company.close_price) + '</span>');
                unfocus_companies.append(btn);
            }
            else {
                let btn = $('<span id="' + company.code + '" class="company-button red-button">' +
                    company.code + company.name + ' ' + count_percentage(company.open_price, company.close_price) + '</span>');
                unfocus_companies.append(btn);

            }
    });
    _brokers.map(function (broker, i) {
        if (broker.focus)
            focus_brokers.append("<span id='" + broker.code + "' class='broker-button'>" + broker.code +
                broker.name + "</span>");
        else
            unfocus_brokers.append("<span id='" + broker.code + "' class='broker-button'>" + broker.code +
                broker.name + "</span>");
    });

    // empty
    content.append(info_bar);
    content_home.append(focus_companies);
    content_home.append(focus_brokers);
    content_home.append(unfocus_companies);
    content_home.append(unfocus_brokers);
    content.append(content_home);
    waiting.remove();
}

function render_content_company() {
    // empty
    content.empty();

    let waiting = $('<div class="waiting">Waiting...</div>');
    content.append(waiting);

    // toolbar
    let toolbar = $('<div class="toolbar"></div>');
    content.append(toolbar);

    // toolbar - date search
    let date_toolbar = $('<span class="date-toolbar"></span>');
    let s_date_picker = $('<span><input type="text" id="start-date-picker" placeholder="Start date..." class="date-picker"></span>');
    let e_date_picker = $('<span><input type="text" id="end-date-picker" placeholder="End date..." class="date-picker"></span>');
    let search = $('<span class="toolbar-btn toolbar-search">SEARCH</span>');
    date_toolbar.append(s_date_picker);
    date_toolbar.append(e_date_picker);
    date_toolbar.append(search);
    toolbar.append(date_toolbar);

    //
    let parts = s_e_date[0].split('-');
    let s_date = new Date(parseInt(parts[0]), parseInt(parts[1] - 1), parseInt(parts[2]));
    $('#start-date-picker').datepicker({
        onSelect: function(dateText, inst) {
            s_e_date[0] = dateText;
        },
        dateFormat: 'yy-mm-dd'
    }).datepicker("setDate", s_date);
    parts = s_e_date[1].split('-');
    let e_date = new Date(parseInt(parts[0]), parseInt(parts[1] - 1), parseInt(parts[2]));
    $('#end-date-picker').datepicker({
        onSelect: function(dateText, inst) {
            s_e_date[1] = dateText;
        },
        dateFormat: 'yy-mm-dd'
    }).datepicker("setDate", e_date);

    // toolbar - sort
    let sort_toolbar = $('<span class="sort-toolbar"></span>');
    let items_select = $('<select class="toolbar-btn toolbar-select">' +
        '<option value="25">25</option>' +
        '<option value="50">50</option>' +
        '<option value="100">100</option></select>');
    let buy_btn = $('<span class="toolbar-btn toolbar-sort-buy">BUY</span>');
    let sell_btn = $('<span class="toolbar-btn toolbar-sort-sell">SELL</span>');
    let amount_btn = $('<span class="toolbar-btn toolbar-sort-amount">AMOUNT</span>');
    let pos_acc_amount_btn = $('<span class="toolbar-btn toolbar-sort-pos-acc-amount">+ACC AMOUNT</span>');
    let neg_acc_amount_btn = $('<span class="toolbar-btn toolbar-sort-neg-acc-amount">-ACC AMOUNT</span>');
    let focus_btn = $('<span class="toolbar-btn toolbar-sort-focus">FOCUS</span>');
    sort_toolbar.append(items_select, buy_btn, sell_btn, amount_btn, pos_acc_amount_btn, neg_acc_amount_btn, focus_btn);
    toolbar.append(sort_toolbar);

    let info_bar = $("<div class='info-bar'>DATE: " + data_date + ", QUERY: " + query_time + "</div>");
    content.append(info_bar);
    $('.toolbar-select').val(render_items.toString());

    // company - title
    let company_title = $('<div id="title-' + _company.company.code + '" class="company-title"></div>');
    let title_text = $('<span>' + _company.company.code + ' ' + _company.company.name + '</span>');
    let focus = $('<span> ' + get_focus_star(_company.company.focus) +'</span>');
    company_title.append(title_text);
    company_title.append(focus);
    content.append(company_title);

    // menu - company scroller
    render_menu();
    let menu_company_scroller = $('<div id="menu-' + _company.company.code + '" class="menu-item menu-scroller">' +
        _company.company.code + ' ' + _company.company.name + ' ' + get_focus_star(_company.company.focus) +  '</div>');
    menu.append(menu_company_scroller);

    // company - price/amount chart
    let w = 50 + _company.company.data.length * 35;
    let price_chart = $('<div id="price-chart-' + _company.company.code + '" style="height:200px;width:' + w + 'px;"></div>');
    w = 50 + _company.company.data.length * 35 + 28;
    let amount_chart = $('<div id="amount-chart-' + _company.company.code + '" style="height:200px;width:' + w + 'px;"></div>');
    content.append(price_chart);
    content.append(amount_chart);

    $.jqplot('price-chart-' + _company.company.code, [_company.company.data],{
      axes: {
          xaxis: {
              renderer: $.jqplot.CategoryAxisRenderer,
              tickOptions: {fontSize: '8pt'},
          },
          yaxis: {
            tickOptions: {formatString: '%.2f'},
            min: parseFloat(_company.company.min_price),
            max: parseFloat(_company.company.max_price)
          }
      },
      series: [{
          renderer:$.jqplot.OHLCRenderer,
          rendererOptions:{
              candleStick:true,
              fillUpBody: true,
              fillDownBody: true,
              upBodyColor: "rgba(222, 47, 47, 0.8)",
              downBodyColor: "rgba(15, 101, 15, 0.8)",
              bodyWidth: 8
          },
          pointLabels: { show: false }

      }],
      highlighter: {
          showMarker:false,
          tooltipAxes: 'xy',
          yvalues: 5,
          formatString:'<table class="jqplot-highlighter"> \
          <tr><td>date:</td><td>%s</td></tr> \
          <tr><td>open:</td><td>%#.2f</td></tr> \
          <tr><td>hi:</td><td>%.2f</td></tr> \
          <tr><td>low:</td><td>%.2f</td></tr> \
          <tr><td>close:</td><td>%.2f</td></tr>'
      }
    });

    $.jqplot('amount-chart-' + _company.company.code, [_company.company.amount, _company.company.percentage], {
        seriesColors: _company.company.color,
        series:[
            {
                renderer: $.jqplot.BarRenderer,
                pointLabels: {show: true, formatString: '%s'},
                rendererOptions: {varyBarColor: true, barWidth: 8},
                yaxis: 'yaxis',
            },
            {
                pointLabels: {show: true, formatString: '%s%'},
                color: 'rgba(63, 127, 191, 0.8)',
                yaxis: 'y2axis',

            },
        ],
        axes: {
            xaxis: {
                renderer: $.jqplot.CategoryAxisRenderer,
                ticks: _company.company.date,
                tickOptions: {fontSize: '8pt'},
            },
            yaxis: {
                tickOptions: {formatString: '%05d'}
            },
            y2axis: {
                tickOptions: {formatString: '%01d'},
                min: -10,
                max: 10
            },
        },
        cursor:{
          zoom:false,
          tooltipOffset: 10,
          tooltipLocation: 'nw'
        },
        highlighter: { show: false }
    });

    // brokers
    for (let i = 0; i < _company.brokers.length; i++) {
        if (i > render_items)
            break;

        let broker = _company.brokers[i];

        // broker - title
        let broker_title = $('<div id="title-' + broker.code + '" class="broker-title"></div>');
        let title_text = $('<span>' + broker.code + ' ' + broker.name + '</span>');
        let focus = $('<span> ' + get_focus_star(broker.focus) + '</span>');
        let summaries = $('<span class="summaries"></span>');
        summaries.append('<span class="summary red-font">' + broker.buy_amount_sum + '</span>');
        summaries.append('<span class="summary green-font">' + broker.sell_amount_sum + '</span>');
        summaries.append('<span class="summary">' + broker.all_amount_sum + '</span>');
        summaries.append('<span class="summary">' + broker.acc_amount_sum + '</span>');
        broker_title.append(title_text);
        broker_title.append(focus);
        broker_title.append(summaries);
        content.append(broker_title);

        // menu - company scroller
        let menu_broker_scroller = $('<div id="menu-' + broker.code + '" class="menu-item menu-scroller">' +
            broker.code + ' ' + broker.name + ' ' + get_focus_star(broker.focus) +  '</div>');
        menu.append(menu_broker_scroller);

        // broker - buy sell amount chart
        w = 50 + _company.company.data.length * 35;
        let bs_amount_chart = $('<div id="bs-amount-chart-' + broker.code + '" style="height:200px;width:' + w + 'px;"></div>');
        content.append(bs_amount_chart);

        $.jqplot('bs-amount-chart-' + broker.code, [broker.buy_amount, broker.sell_amount], {
            seriesColors:["rgba(222, 47, 47, 0.8)", "rgba(15, 101, 15, 0.8)"],
            seriesDefaults: {
                renderer: $.jqplot.BarRenderer,
                pointLabels: { show: true, formatString: '%s', edgeTolerance: -10, ypadding: 5, fontSize: '8pt'},
                yaxis: 'yaxis',
                rendererOptions: {barMargin: 0, barWidth: 2},
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: broker.date,
                    tickOptions: {fontSize: '8pt'},
                },
                yaxis: {
                    tickOptions: {formatString: '%05d'}
                }
            },
            cursor:{
                zoom:false,
                tooltipOffset: 10,
                tooltipLocation: 'nw'
            },
            highlighter: { show: false }
        });
    }

    // remove waiting
    waiting.remove();

}

function render_content_broker() {
    // empty
    content.empty();

    // toolbar
    let toolbar = $('<div class="toolbar"></div>');
    content.append(toolbar);

    // toolbar - date search
    let date_toolbar = $('<span class="date-toolbar"></span>');
    let s_date_picker = $('<span><input type="text" id="start-date-picker" placeholder="Start date..." class="date-picker"></span>');
    let e_date_picker = $('<span><input type="text" id="end-date-picker" placeholder="End date..." class="date-picker"></span>');
    let search = $('<span class="toolbar-btn">SEARCH</span>');
    date_toolbar.append(s_date_picker);
    date_toolbar.append(e_date_picker);
    date_toolbar.append(search);
    toolbar.append(date_toolbar);

    // toolbar - sort
    let sort_toolbar = $('<span class="sort-toolbar"></span>');
    let buy_btn = $('<span class="toolbar-btn toolbar-sort-buy">BUY</span>');
    let sell_btn = $('<span class="toolbar-btn toolbar-sort-sell">SELL</span>');
    let amount_btn = $('<span class="toolbar-btn toolbar-sort-amount">AMOUNT</span>');
    let pos_acc_amount_btn = $('<span class="toolbar-btn toolbar-sort-pos-acc-amount">+ACC AMOUNT</span>');
    let neg_acc_amount_btn = $('<span class="toolbar-btn toolbar-sort-neg-acc-amount">-ACC AMOUNT</span>');
    let focus_btn = $('<span class="toolbar-btn toolbar-sort-focus">FOCUS</span>');
    sort_toolbar.append(buy_btn, sell_btn, amount_btn, pos_acc_amount_btn, neg_acc_amount_btn, focus_btn);
    toolbar.append(sort_toolbar);

    // broker - title
    let broker_title = $('<div id="title-' + test_broker.broker.code + '" class="broker-title"></div>');
    let title_text = $('<span>' + test_broker.broker.code + ' ' + test_broker.broker.name + '</span>');
    let focus = $('<span> ' + get_focus_star(test_broker.broker.focus) + '</span>');
    broker_title.append(title_text);
    broker_title.append(focus);
    content.append(broker_title);

    // menu - company scroller
    render_menu();
    let menu_broker_scroller = $('<div id="menu-' + test_broker.broker.code + '" class="menu-item menu-scroller">' +
        test_broker.broker.code  + ' ' + test_broker.broker.name  + ' ' + get_focus_star(test_broker.broker.focus) +  '</div>');
    menu.append(menu_broker_scroller);

    // companies
    test_broker.companies.map(function(company, i) {

        // company - title
        let company_title = $('<div id="title-' + company.code + '" class="company-title"></div>');
        let title_text = $('<span>' + company.code + ' ' + company.name + '</span>');
        let focus = $('<span> ' + get_focus_star(company.focus)+ '</span>');
        company_title.append(title_text);
        company_title.append(focus);
        content.append(company_title);

        // menu -scroller
        let menu_company_scroller = $('<div id="menu-' + company.code + '" class="menu-item menu-scroller">' +
            company.code + ' ' + company.name + ' ' + get_focus_star(company.focus) +  '</div>');
        menu.append(menu_company_scroller);

        // company - price/amount chart
        let w = 50 + company.date.length * 35;
        let price_chart = $('<div id="price-chart-' + company.code + '" style="height:200px;width:' + w + 'px;"></div>');
        w = 50 + _company.company.data.length * 35 + 28;
        let amount_chart = $('<div id="amount-chart-' + company.code + '" style="height:200px;width:' + w + 'px;"></div>');
        content.append(price_chart);
        content.append(amount_chart);

        $.jqplot('price-chart-' + company.code, [company.data],{
              axes: {
                  xaxis: {
                      renderer: $.jqplot.CategoryAxisRenderer,
                      tickOptions: {fontSize: '8pt'},
                  },
                  yaxis: {
                    tickOptions: {formatString: '%.2f'},
                    min: 22,
                    max: 31,
                  }
              },
              series: [{
                  renderer:$.jqplot.OHLCRenderer,
                  rendererOptions:{
                      candleStick:true,
                      fillUpBody: true,
                      fillDownBody: true,
                      upBodyColor: "rgba(222, 47, 47, 0.8)",
                      downBodyColor: "rgba(15, 101, 15, 0.8)",
                      bodyWidth: 8
                  },
                  pointLabels: { show: false }

              }],
              highlighter: {
                  showMarker:false,
                  tooltipAxes: 'xy',
                  yvalues: 5,
                  formatString:'<table class="jqplot-highlighter"> \
                  <tr><td>date:</td><td>%s</td></tr> \
                  <tr><td>open:</td><td>%#.2f</td></tr> \
                  <tr><td>hi:</td><td>%.2f</td></tr> \
                  <tr><td>low:</td><td>%.2f</td></tr> \
                  <tr><td>close:</td><td>%.2f</td></tr>'
              }
            });
            $.jqplot('amount-chart-' + company.code, [company.amount, company.percentage], {
                seriesColors: company.color,
                series:[
                    {
                        renderer: $.jqplot.BarRenderer,
                        pointLabels: {show: true, formatString: '%s'},
                        rendererOptions: {varyBarColor: true, barWidth: 8},
                        yaxis: 'yaxis',
                    },
                    {
                        pointLabels: {show: true, formatString: '%s%'},
                        color: 'rgba(63, 127, 191, 0.8)',
                        yaxis: 'y2axis',
                    },
                ],
                axes: {
                    xaxis: {
                        renderer: $.jqplot.CategoryAxisRenderer,
                        ticks: company.date,
                        tickOptions: {fontSize: '8pt'},
                    },
                    yaxis: {
                        tickOptions: {formatString: '%05d'}
                    },
                    y2axis: {
                    },
                },
                cursor:{
                  zoom:false,
                  tooltipOffset: 10,
                  tooltipLocation: 'nw'
                },
                highlighter: { show: false }
            });

            // company - buy sell amount chart
            w = 50 + company.date.length * 35;
            let bs_amount_chart = $('<div id="bs-amount-chart-' + company.code + '" style="height:200px;width:' + w + 'px;"></div>');
            content.append(bs_amount_chart);

            $.jqplot('bs-amount-chart-' + company.code, [company.buy_amount, company.sell_amount, company.all_amount, company.acc_amount], {
                seriesColors:["rgba(222, 47, 47, 0.8)", "rgba(15, 101, 15, 0.8)", "rgba(63, 127, 191, 0.8)", "rgba(214, 122, 30, 0.8)"],
                seriesDefaults: {
                    renderer: $.jqplot.BarRenderer,
                    pointLabels: { show: true, formatString: '%s', edgeTolerance: -10, ypadding: 5, fontSize: '8pt'},
                    yaxis: 'yaxis',
                    rendererOptions: {barMargin: 0, barWidth: 2},
                },
                axes: {
                    xaxis: {
                        renderer: $.jqplot.CategoryAxisRenderer,
                        ticks: company.date,
                        tickOptions: {fontSize: '8pt'},
                    },
                    yaxis: {
                        tickOptions: {formatString: '%05d'}
                    }
                },
                cursor:{
                  zoom:false,
                  tooltipOffset: 10,
                  tooltipLocation: 'nw'
                },
                highlighter: { show: false }
            });

    });
}

// setup

function setup() {

    $.jqplot.config.enablePlugins = true;

    // menu

    body.on('click', '#menu-home', function() {
        selected[0] = "home";
        selected[1] = null;
        render_menu();
        render_content_home();
    });

    body.on('click', '.menu-scroller', function() {
        let title = 'title-' + $(this).attr('id').slice(5);
        $('html,body').animate({
            scrollTop: $("#" + title).offset().top
        });
    });

    // home content

    body.on('click',".company-button", function() {
        selected[0] = "company";
        selected[1] = $(this).attr('id');
        ajax_api_2();
    });

    body.on('click',".broker-button", function() {
        selected[0] = "broker";
        selected[1] = $(this).attr('id');
        render_content_broker();
    });

    // toolbar

    body.on('focus', '#start-date-picker', function() {
        $(this).datepicker({
            onSelect: function (dateText, inst) {
                s_e_date[0] = $(this).datepicker("getDate").toISOString().slice(0, 10);
                console.log(s_e_date[0]);
            }
        });
    });


    body.on('focus', '#end-date-picker', function() {
        $(this).datepicker({
            onSelect: function (dateText, inst) {
                s_e_date[1] = $(this).datepicker("getDate").toISOString().slice(0, 10);
                console.log(s_e_date[1]);
            }
        });
    });

    body.on('change',".toolbar-select", function() {
        render_items = parseInt($(this).val());

        if (selected[0] === 'company')
            render_content_company();
        else if (selected[0] === 'broker')
            render_content_broker();
    });

    body.on('click',".toolbar-search", function() {
        if (selected[0] === 'company')
            ajax_api_2();
        else if (selected[0] === 'broker')
            ajax_api_2();
    });

    // toolbar

    body.on('click',".toolbar-sort-buy", function() {
        alert('sort buy: ' + selected + s_e_date);

        if (selected[0] === 'company')
            render_content_company();
        else if (selected[0] === 'broker')
            render_content_broker();
    });


    body.on('click',".toolbar-sort-sell", function() {
        alert('sort sell: ' + selected + s_e_date);

        if (selected[0] === 'company')
            render_content_company();
        else if (selected[0] === 'broker')
            render_content_broker();
    });

    body.on('click',".toolbar-sort-amount", function() {
        alert('sort amount: ' + selected + s_e_date);

        if (selected[0] === 'company')
            render_content_company();
        else if (selected[0] === 'broker')
            render_content_broker();
    });

    body.on('click',".toolbar-sort-pos-acc-amount", function() {
        alert('sort pos acc amount: ' + selected + s_e_date);

        if (selected[0] === 'company')
            render_content_company();
        else if (selected[0] === 'broker')
            render_content_broker();
    });

    body.on('click',".toolbar-sort-neg-acc-amount", function() {
        alert('sort neg acc amount: ' + selected + s_e_date);

        if (selected[0] === 'company')
            render_content_company();
        else if (selected[0] === 'broker')
            render_content_broker();
    });

    body.on('click',".toolbar-sort-focus", function() {
        alert('sort focus: ' + selected + s_e_date);

        if (selected[0] === 'company')
            render_content_company();
        else if (selected[0] === 'broker')
            render_content_broker();
    });
}

// ajax

function ajax_api_1() {
    // empty
    content.empty();
    
    let waiting = $('<div class="waiting">Waiting...</div>');
    content.append(waiting);

    $.get( "/api1", function( data ) {
        // query time
        query_time = Math.round(parseFloat(data['query_time']) * 100) / 100;

        // date
        data_date = data['date'];

        // companies
        data.companies.map(function (company, i) {
            _companies.push({
                code: company[0],
                name: company[1],
                open_price: parseFloat(company[3]),
                close_price: parseFloat(company[4]),
                focus: parseInt(company[2])
            });
        });

        //brokers
        data.brokers.map(function (broker, i) {
            _brokers.push({
                code: broker[0],
                name: broker[1],
                focus: broker[2]
            });
        });

        // render
        render_content_home();
    });
}

function ajax_api_2() {

    // empty
    content.empty();

    let waiting = $('<div class="waiting">Waiting...</div>');
    content.append(waiting);

    // set date
    if (s_e_date[0] == null || s_e_date[1] == null) {
        let parts = data_date.split('-');
        let e_date = new Date(parseInt(parts[0]), parseInt(parts[1] - 1), parseInt(parts[2]));
        let s_date = new Date(e_date.getTime() - (30 * 24 * 60 * 60 * 1000));
        s_e_date = [s_date.toISOString().slice(0, 10), e_date.toISOString().slice(0, 10)];
    }

    // get chart data
    let data = {
        'type': selected[0],
        'code': selected[1],
        's_date': s_e_date[0],
        'e_date': s_e_date[1]
    };
    $.post( "/api2", JSON.stringify(data), function( data ) {
        // query time
        query_time = Math.round(parseFloat(data['query_time']) * 100) / 100;

        // company
        _company['company'] = data['company'];
        _company['company']['color'] = [];
        _company['company']['percentage'] = [];
        _company['company']['min_price'] = 1000000;
        _company['company']['max_price'] = 0;

        _company.company.data.map(function (row, i) {
            _company['company']['color'].push(get_red_green(row[1], row[4]));
            if (i == 0)
                _company['company']['percentage'].push(0);
            else
                _company['company']['percentage'].push(count_percentage_float(_company.company.data[i-1][4], row[4]));
            if (row[3] < _company['company']['min_price'])
                _company['company']['min_price'] = row[3];
            if (row[2] > _company['company']['max_price'])
                _company['company']['max_price'] = row[2];
        });

        _company.company.min_price = parseFloat(_company.company.min_price);
        _company.company.max_price = parseFloat(_company.company.max_price);

        let gap = (_company.company.max_price - _company.company.min_price) * 0.1;
        _company.company.min_price = _company.company.min_price - gap;
        _company.company.max_price = _company.company.max_price + gap;
        _company.company.min_price = Math.floor(_company.company.min_price * 100) / 100;
        _company.company.max_price = Math.ceil(_company.company.max_price * 100) / 100;

        _company['brokers'] = data['brokers'];

        _company['brokers'].map(function (broker, i) {
            broker['all_amount'] = [];
            broker['acc_amount'] = [];
            broker['buy_amount_sum'] = 0;
            broker['sell_amount_sum'] = 0;
            broker['all_amount_sum'] = 0;
            broker['acc_amount_sum'] = 0;

            for (let j = 0; j < broker.date.length; j ++) {
                broker['all_amount'].push(parseInt(broker['buy_amount'][j]) + parseInt(broker['sell_amount'][j]));
                broker['acc_amount'].push(parseInt(broker['buy_amount'][j]) - parseInt(broker['sell_amount'][j]));
                broker['buy_amount_sum'] += parseInt(broker['buy_amount'][j]);
                broker['sell_amount_sum'] += parseInt(broker['sell_amount'][j]);
                broker['all_amount_sum'] += parseInt(broker['buy_amount'][j]) + parseInt(broker['sell_amount'][j]);
                broker['acc_amount_sum'] += parseInt(broker['buy_amount'][j]) - parseInt(broker['sell_amount'][j]);
            }
        });

        // render
        render_menu();
        render_content_company();
    });

}


// util

function count_percentage(open_price, close_price) {
    if (close_price - open_price < 0)
        return (Math.round((close_price - open_price) / open_price * 1000) / 10).toString() + '%';
    else
        return '+' +  (Math.round((close_price - open_price) / open_price * 1000) / 10).toString() + '%';
}

function count_percentage_float(open_price, close_price) {
    return Math.round((close_price - open_price) / open_price * 1000) / 10;
}

function get_focus_star(focus) {
    if (focus)
        return '&#x2605';
    else
        return '&#x2606';
}

function get_red_green(open_price, close_price) {
    if (close_price - open_price < 0)
        return "rgba(15, 101, 15, 0.8)";
    else
        return "rgba(222, 47, 47, 0.8)";
}



