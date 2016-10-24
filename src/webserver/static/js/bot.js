$(function() {
   var ws;
   var $input = $('input[name="chatbox-input-text"]');
   var $send_button = $('input[name="chatbot-input-send"]');
   var chatbox_output = document.getElementById('chatbox-output');
   var $output_table = $('#chatbox-output .output-table > tbody');

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
         var msgs = generate_msgs(msg);
         row = msgs.join('');
      }
      
      var last_tr = $output_table.find('>tr:last-child');
      if (!last_tr.length) {
         $output_table.append(row);
      } else {
         last_tr.after(row);
      }

      // reset height auto
      chatbox_output.scrollTop = chatbox_output.scrollHeight;
   }

   $input.on('change', function(e) {
      send_message();
   });

   $send_button.on('click', function(e) {
      send_message();
   });

});
