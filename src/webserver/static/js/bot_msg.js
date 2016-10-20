function generate_msgs(raw_msg) {
   var data = null;
   try {
      var data = JSON.parse(raw_msg);
   
      var scraper = data.scraper;
      var source = data.source;
      var content = data.content;
      var BotMsgType = bot_msg_types[scraper];
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
      return [render_generic_msg(raw_msg)];
   }

}

var bot_msg_types = {
   'finance': BotFinanceMsg,
   'weather': BotWeatherMsg
}

function render_generic_msg(msg) {
   return '<tr class="bot"><td class="msg bot">' + msg + '</td></tr>';
}

//generic finance msg
function BotFinanceMsg(msg) {
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
      
      var card = build_msg_card(config);

      return '<tr class="bot"><td class="msg bot finance">' + card.outerHTML + '</td></tr>';
   }

   $.extend(this, {
      'render': render
   });
}

//generic weather msg
function BotWeatherMsg(msg) {
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
      
      var card = build_msg_card(config);

      return '<tr class="bot"><td class="msg bot">' + card.outerHTML + '</td></tr>';
   }

   $.extend(this, {
      'render': render
   });
}

function build_msg_card(config) {
   var width = config.width || 300;
   var id = config.id;
   var items = config.items;
   var num_cols = config.num_cols;

   //each cell is a square
   var px_per_col = width/num_cols;      
   var px_per_row = px_per_col/2;

   var card = document.createElement('div');
   card.style['width'] = width + 'px';
   card.style['display'] = 'block';
      
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
      
   return card;
}
