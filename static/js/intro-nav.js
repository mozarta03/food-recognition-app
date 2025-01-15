var counter = 1;
var interval = 5000;

setInterval(function(){
   for(let i = 1; i <= 4; i++){
       if(document.getElementById('radio' + i).checked){
           counter = i;
           break;
       }
   }
    counter++;
    if(counter > 4){
        counter = 1;
    }
    document.getElementById('radio' + counter).checked = true;
}, interval);