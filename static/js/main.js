const fillProductChoices = () => {
    console.log(state);
    let selector = document.getElementById('google-product-category-choices');
    selector.onclick = (event) => {
        event.stopPropagation();
    };

    const closeMenu = () => {
        selector.classList.remove("show");
    };
    let choices = google_product_categories;

    // iterate through previous state to find current list to show
    for (let s of state) {
        let nextSet = choices[s];
        console.log("Next Set");
        console.log(nextSet);
        if (nextSet === undefined) {
            break;
        }
        choices = nextSet;
    }
    console.log(choices);

    selector.innerHTML = ''; // empty the menu of items in case there were previous ones

    // if there is previous state, need a back button (state length > 1)
    if (state.length >= 1) {
        // Current sub-category/category you are in
        const header = document.createElement('h6');
        header.className = "dropdown-header";
        header.innerHTML = state[state.length - 1];
        selector.appendChild(header);

        // Back button
        const backButton = document.createElement('button');
        backButton.type = "button";
        backButton.innerHTML = "< Back";
        backButton.className = "dropdown-item";
        backButton.onclick = () => {
            state.pop();
            fillProductChoices();
        };
        selector.appendChild(backButton);
    }

    for (let choice in choices) {
        if (choice === "id") {
            continue;
        }
        const isLeaf = Object.keys(choices[choice]).length <= 1;

        let option = document.createElement('button');
        option.type = "button";
        if (!isLeaf) {
            option.innerHTML = choice + " >";
        } else {
            option.innerHTML = choice;
        }
        option.className = "dropdown-item";
        option.onclick = () => {
            if (isLeaf) {
                const buttonText = document.getElementById('google-product-category-button');
                buttonText.innerHTML = choice;

                // update hidden field for form with id
                const hiddenFieldId = document.getElementById('google-product-category-id');
                hiddenFieldId.value = choices[choice]["id"];
                const hiddenFieldString = document.getElementById('google-product-category-string');
                hiddenFieldString.value = [...state, choice].join(" > ");

                closeMenu();
            } else {
                state.push(choice);
                fillProductChoices();
            }
        };

        selector.appendChild(option);

    }
}
