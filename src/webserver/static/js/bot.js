$(function() {
   var ws;
   var $input = $('input[name="chatbox-input-text"]');
   var $send_button = $('input[name="chatbot-input-send"]');
   var $output = $('#chatbox-output table');

   ws = new WebSocket("ws://localhost:8000/ws/bot");

   ws.onopen = function(e) {
      console.log('open socket');
   }

   ws.onclose = function(e) {
      console.log('closing socket');
   };

   ws.onerror = function(e) {
      console.log(e);
   }

   ws.onmessage = function(e) {
      append_message(e.data, 'bot');
   };

   function send_message() {
      var msg = $input.val();
      $input.val('');
      if (msg === '') {return;}      
      append_message(msg, 'user');
      ws.send(msg);
   };

   function append_message(msg, owner) {
      var row = '';
      if (owner === 'user') {
         row = '<tr class="user"><td class="msg user">' + msg + '</td></tr>';
      } else {
         row = '<tr class="bot"><td class="msg bot">' + msg + '</td></tr>'; 
      }

      $output.append(row);
   }

   $input.on('change', function(e) {
      send_message();
   });

   $send_button.on('click', function(e) {
      send_message();
   });

});
