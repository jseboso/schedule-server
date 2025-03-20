// Sebas Osorio
// clock logic
function clock() {
   var datetoday = new Date();
   var timenow = datetoday.toLocaleTimeString();
   var hourRaw = datetoday.getHours();
   var hour = hourRaw;
   var minuteRaw = datetoday.getMinutes();
   var minutes = minuteRaw;
   var secondRaw = datetoday.getSeconds();
   var seconds = secondRaw;
   var amPmCheck = "AM";
   // format hours
   if (hourRaw == 0) {
      hour = 12;
   } else if (hourRaw > 12) {
      hour = hourRaw - 12;
   }
   if (hourRaw >= 12) {
      amPmCheck = "PM";
   }
   // format minutes
   if (minuteRaw <= 9) {
      minutes = minuteRaw.toString().padStart(2, '0');
   }
   // format seconds
   if (secondRaw <= 9) {
      seconds = secondRaw.toString().padStart(2, '0');
   }

   document.getElementById("currentHour").textContent = hour;
   document.getElementById("currentMinute").textContent = minutes;
   document.getElementById("currentSecond").textContent = seconds;
   document.getElementById("AMorPM").textContent = amPmCheck;
}

var intID = setInterval(function () { clock() }, 1000);