const resetForm = document.getElementById('reset-form');
if (resetForm) {
 resetForm.addEventListener("submit",function(event){
  const continueReset=confirm("Are you sure you want to reset the current season?")
  if (continueReset==false){
   event.preventDefault();
  }
 });
}
const winnerMessage = document.getElementById("winner-message");
if (winnerMessage) {
    const winner = winnerMessage.dataset.winner;
    alert(`Congratulations! ${winner} won the Premier League!`);
}