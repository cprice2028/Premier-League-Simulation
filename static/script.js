const resetForm = document.getElementById('reset-form')
if (resetForm) {
  resetForm.addEventListener('submit', function (event) {// when pressed reset season button
    const continueReset = confirm(
      'Are you sure you want to reset the current season?'
    ) // prompt the user to confirm
    if (continueReset == false) { // if the user doesnt confirm, then prevent the action from happening
      event.preventDefault()
    }
    else {
        localStorage.removeItem(winnerAlert) //season reset, allow winner alerts
    }
  })
}
const winnerMessage = document.getElementById('winner-message')// find the element containing the winner's name
const winnerAlert = 'premier-league-winner-alert-shown' // name of the value saved in the browser
if (winnerMessage) {
  const winner = winnerMessage.dataset.winner // read the winner from the element's data-winner attribute
  if (localStorage.getItem(winnerAlert) !== 'true') {  // only show the alert if it has not already been shown
    alert(`Congratulations! ${winner} won the Premier League!`)
    localStorage.setItem(winnerAlert, 'true') // store that the alert has shown
  }

}
