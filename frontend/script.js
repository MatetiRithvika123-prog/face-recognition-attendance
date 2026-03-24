function addTask() {
  const taskInput = document.getElementById("taskInput");
  const taskList = document.getElementById("taskList");
  const taskText = taskInput.value.trim();

  if (taskText === "") return;

  const li = document.createElement("li");
  li.textContent = taskText;

  // Optionally: remove task on click
  li.onclick = function () {
    taskList.removeChild(li);
  };

  taskList.appendChild(li);
  taskInput.value = "";
}
