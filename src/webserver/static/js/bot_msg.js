function generate_msgs(raw_msg) {
   var data = null;
   try {
      var data = JSON.parse(raw_msg);
   
      var scraper = data.scraper;
      var source = data.source;
      var content = data.content;
      var BotMsgType = bot_msg_types[source];
      var rendered_msgs = [];

      if (Array.isArray(content)) {   
         //array, loop through and generate multiple msgs
         for (var i=0; i<content.length; i++) {
            var msg = content[i];
            var bot_msg_obj = new BotMsgType(msg);
            rendered_msgs.push(bot_msg_obj.render());
         }
      } else {
         var msg = content;
         var bot_msg_obj = new BotMsgType(msg);
         rendered_msgs.push(bot_msg_obj.render());
      }

      return rendered_msgs;
   } catch(e) {
      console.log(e);
      return [render_generic_msg(raw_msg)];
   }

}

var bot_msg_types = {
   'google_finance_info': GoogleFinanceMsg,   
   'openweather_by_city': WeatherMsg,
   'finviz_stock_info': FinvizInfoMsg,
   'fb_db_standings': FBDBMsg,
   'theguardian_standings': TheGuardianStandingsMsg,
   'sportinglife_fixtures': SportingLifeFixturesMsg,
   'sportinglife_results': SportingLifeResultsMsg
}

function render_generic_msg(msg) {
   return '<tr class="bot"><td class="msg bot">' + msg + '</td></tr>';
}

//TODO: USE CLASS
function build_msg_card(config) {
   var width = config.width || 300;
   var id = config.id;
   var items = config.items;
   var num_cols = config.num_cols;
   var card_style = config.style || {};
   
   //each cell is a square
   var px_per_col = width/num_cols;      
   var px_per_row = px_per_col*0.6;

   var card = document.createElement('div');
   card.style['width'] = width + 'px';
   card.style['display'] = 'block';

   //custom card styles
   for (var k in card_style) {
      if (card_style.hasOwnProperty(k)) {
         card.style[k] = card_style[k];
      };
   }

   for (var i = 0; i < items.length; i++) {
      var item_height = items[i].dimension[0] * px_per_row;
      var item_width = items[i].dimension[1] * px_per_col;
      var item_field = items[i].field;
      var item_text = items[i].text;
      var item_style = items[i].style || {};

      var item = document.createElement('div');
      item.setAttribute('msg-field', item_field);
      item.innerHTML = item_text;
         
      // positional styles
      item.style['width'] = item_width + 'px';
      item.style['height'] = item_height + 'px';
      item.style['display'] = 'block';
      item.style['float'] = 'left';

      //custom styles
      for (var k in item_style) {
         if (item_style.hasOwnProperty(k)) {
            item.style[k] = item_style[k];
         };
      }
         
      card.appendChild(item);
   }  
      
   return '<tr class="bot"><td class="msg bot">' + card.outerHTML + '</td></tr>';
}

function build_table(ths, rows_data, style) {
   var thead = '<thead><tr><th>' + ths.join('</th><th>') + '</th></tr></thead>';
   var rows = [];

   for (var i=0; i<rows_data.length; i++) {
      var tds = rows_data[i];
      rows.push('<tr><td>' + tds.join('</td><td>') + '</td></tr>');
   }
   
   var tbody = '<tbody>' + rows.join('') + '</tbody>';
   var style = style == undefined ? '' : style;

   return '<table style="' + style + '">' + thead + tbody + '</table>';
}

//generic finance msg
function GoogleFinanceMsg(msg) {
   var msg = msg;

   function render() {
      var html = [];
      var symbol = msg.symbol;
      var exchange = msg.exchange;      
      var price  = msg.price;      
      var price_hi = msg.price_hi;
      var price_lo = msg.price_lo;
      var change = msg.change;     
      var direction = change < 0 ? 'neg' : change == 0 ? 'neu' : 'pos';
      var pe = msg.pe;

      var config = {
         width: 250,
         num_cols: 5,
         items: [
            {
               dimension: [2,3],
               field: 'symbol',
               text: symbol + ' (' + exchange + ')',
               style: {
                  'font-weight': '600'
               }
            },
            {
               dimension: [1,2],
               field: 'price',
               text: '<span direction="' + direction + '">' + price + '(' + change + '%)</span>',
               style: {
                  'font-weight': '600'
               }               
            },            
            {
               dimension: [1,2],
               field: 'pe',
               text: 'P/E:' + pe
            },
            {
               dimension: [1,5],
               field: 'price-range',
               text: 'Lo-hi: ' + price_lo + ' - ' + price_hi
            }
         ]
      }
      
      return build_msg_card(config);
   }

   $.extend(this, {
      'render': render
   });
}

//generic weather msg
function WeatherMsg(msg) {
   var msg = msg;

   function render() {
      var html = [];
      
      var city = msg.city_name;
      var temp = (msg.main.temp - 273.15).toFixed(2);
      var humidity = msg.main.humidity;
      var temp_min = (msg.main.temp_min - 273.15).toFixed(2);
      var temp_max = (msg.main.temp_max - 273.15).toFixed(2);
      var icon = msg.weather[0].icon;
      
      var config = {
         width: 250,
         num_cols: 5,
         items: [
            {
               field: 'city',
               dimension: [1,2],
               text: city,
               style: {
                  'font-weight': '600'
               }        
            },
            {
               field: 'temp',
               dimension: [1,3],
               text: temp + '&deg;C'
            },
            {
               field: 'icon',
               dimension: [2,2],
               text: '<img src="http://openweathermap.org/img/w/' + icon  + '.png">'
            },
            {
               field: 'humidity',
               dimension: [1,3],
               text: 'humidity: ' + humidity + '%'
            },            
            {
               field: 'temp-range',
               dimension: [1,3],
               text: temp_min + '&deg;C - ' + temp_max + '&deg;C'
            }
         ]
      }
      
      return build_msg_card(config);
   }

   $.extend(this, {
      'render': render
   });
}

function FinvizInfoMsg(msg) {
   var msg = msg;

   function render() {
      var data = msg.data;
      var chart = msg.chart;      
      var fields = ['Price','Change','Beta','Debt/Eq','P/E','P/B','P/C',
                    'P/FCF','EPS (ttm)','Sales','Income','Market Cap',
                    'Profit Margin', 'Quick Ratio', '52W Range'];

      var config = {
         width: 520,
         num_cols: 10,
         items: [
            {
               field: 'chart',
               dimension: [10,10],
               text: '<img style="height:90%;width:100%" src="'+ chart +'">',
            }
         ]
      }
      
      for (var i=0; i<fields.length; i++) {
         var field = fields[i];
         var val = data[field];
         config.items.push({
            field: field,
            dimension: [1,2],
            text: '<b>' + field + '</b> : ' + val,
            style: {'font-size': '12px', 'padding-top': '3px'}
         });
      }
      
      return build_msg_card(config);
   }

   $.extend(this, {
      'render': render
   });
}

function FBDBMsg(msg) {
   var msg = msg;

   function render() {
      var total = msg.total;
      var home = msg.home;
      var away = msg.away;
      var logos = msg.logos;
      
      var ths = msg.total[0];
      var rows_data = msg.total.slice(1);
      var table_style = 'text-align:left; padding: 3px; width:100%; font-size: 13px';
      var config = {
         width: 600,
         num_cols: 1,
         items: [{
            dimension: [1,1],
            text: build_table(ths, rows_data, table_style),
            field: 'standings',
            style: {'height': 'auto'}
         }],
         style: {
            'max-height': '300px',
            'overflow-y': 'scroll',
            'width': '650px' //50px extra for scroll
         }
      }
   
      
      return build_msg_card(config);
   }

   $.extend(this, {
      'render': render
   });
}

function TheGuardianStandingsMsg(msg) {
   var msg = msg;

   function render() {
      var tables = msg.tables;
      
      var config = {
         width: 600,
         num_cols: 1,
         items: [],
         style: {
            'max-height': '300px',
            'overflow-y': 'scroll',
            'width': '650px' //50px extra for scroll
         }
      }

      for (var i=0; i<tables.length; i++) {
         var table = tables[i];
         var ths = table[0];
         var rows_data = table.slice(1);
         var table_style = 'text-align:left; padding: 3px; width:100%; font-size:13px';

         config.items.push({
            dimension: [1,1],
            text: build_table(ths, rows_data, table_style),
            field: 'standings',
            style: {'height': 'auto'}
         });
      }
      
      return build_msg_card(config);
   }

   $.extend(this, {
      'render': render
   });
}

function SportingLifeFixturesMsg(msg) {
   var msg = msg;

   function render() {
      var game_days = msg.game_days;
      var config = {
         width: 600,
         num_cols: 10,
         items: [],
         style: {
            'max-height': '300px',
            'overflow-y': 'scroll',
            'width': '650px' //50px extra for scroll
         }
      }

      var table_style = 'text-align:left; padding: 3px; width:100%; font-size:13px';
      for (var i=0; i < game_days.length; i++) {
         var game_day = game_days[i];      
         var date = game_day.date;
         var games = game_day.games;
      
         var ths = ['time', 'home', 'away'];
         var rows_data = [];

         for (var j=0; j<games.length; j++) {
            var game = games[j];
            rows_data.push([game.time, game.teams[0], game.teams[1]]);
         }
      
         config.items.push({
            dimension: [1,10],
            field: 'game_day',
            text: '<b>' + date + '</b>',
            style: {'text-align': 'center'}
         });
         
         config.items.push({
            dimension: [10,10],
            text: build_table(ths, rows_data, table_style),
            field: 'fixtures',
            style: {'height': 'auto'}
         });
      }
      
      return build_msg_card(config);
   }

   $.extend(this, {
      'render': render
   });
}


function SportingLifeResultsMsg(msg) {
   var msg = msg;

   function render() {
      var game_days = msg.game_days;
      var config = {
         width: 600,
         num_cols: 12,
         items: [],
         style: {
            'max-height': '300px',
            'overflow-y': 'scroll',
            'width': '650px', //50px extra for scroll
            'font-size': '13px'
         }
      }
      
      console.log(game_days);
      for (var i=0; i<game_days.length; i++) {
         var game_day = game_days[i];
         var date = game_day.date;
         var games = game_day.games;      

         config.items.push({
            dimension: [1,12],
            field: 'game_day',
            text: '<b>' + date + '</b>',
            style: {'text-align': 'center'}
         });

         for (var j=0; j<games.length; j++) {
            var game = games[j];
            var game_items = [
               {
                  dimension: [1,5],
                  field: 'home_team',
                  text: game.teams[0][0]
               },
               {
                  dimension: [1,2],
                  field: 'score',
                  text: game.teams[0][2] + ' - ' + game.teams[1][2],
                  style: {'font-size': '14px', 'font-weight': '600'}
               },
               {
                  dimension: [1,5],
                  field: 'away_team',
                  text: game.teams[1][0]
               }
            ];
            config.items = [].concat.apply(config.items, game_items);
         }     
      }     

      return build_msg_card(config);
   }

   $.extend(this, {
      'render': render
   });
}
