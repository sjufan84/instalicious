""" Example posts for users to get inspiration from """
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(
    page_title="DALL-E 3 Examples", page_icon=":camera_flash:",
    initial_sidebar_state="collapsed"
)

def main():
    with stylable_container(
        key="examples-home",
        css_styles="""
            h3, h5 {
                font-family: 'Arapey', serif;
            }
        """,
    ):
        st.markdown("### Example Posts")

        prompts_list = [
            "california roll, bartop, craft cocktail, speakeasy", """
            *Notice below, the user pasted a recipe to generate a post from.*\n
            **WHY I LOVE THIS RECIPE:**\n
            Arroz Caldo is also known as chicken congee or porridge, a comfort food that
            mirrors the traditional chicken noodle soup.
            What makes it special is the addition of ginger which gives it a nice depth of flavor and warmth.
            ________________________________________
            **INGREDIENTS YOU'LL NEED**\n
            12-16 cups of homemade chicken stock\n
            1 tablespoon minced garlic\n
            1 onion, chopped\n
            1 1/2 tablespoons minced ginger\n
            oil for sauteeing\n
            1 tablespoon black pepper\n
            2 chicken bullion cubes\n
            1 rotisserie chicken deboned\n
            1 1/2 cups rice - sushi, jasmine or long grain\n
            1/4 cup lemon juice\n
            1 handful chopped parsley
            ________________________________________
            **DIRECTIONS**\n
            In large dutch oven, saute garlic, onions and ginger in cooking oil.
            Cook until onions are softened.
            ________________________________________
            Add chicken to pot and heat through. Add rice and stir to
            coat with oil. Add black pepper and bullion cubes. Add homemade chicken stock and stir.
            ________________________________________
            Let it cook over low to medium heat for about 30-40 minutes,
            stirring occassionally. Add lemon juice and chopped parley about 5 minutes before serving.
            """,
            """My friends and I had the best experience at Friendly's bar and grill!  The burger was
            perfect, the fries crispy, and the Guiness ice cold.  Can't wait to go back!"""
        ]

        original_images_list = [
            None, "./resources/original_images/arroz_original.jpeg",
            "./resources/original_images/friendlys_original.jpg"
        ]

        posts_list = [
            """Dive into the heart of culinary magic with our latest adventure
            - a fusion that blends the traditional California roll with the allure
            of a speakeasy bar top and the sophistication of a craft cocktail. Imagine
            the freshness of the California roll, with its creamy avocado,
            crisp cucumber, and tender crab meat, paired with a meticulously
            crafted cocktail that whispers tales of prohibition and mystery.
            🍣🍸 This isn't just a meal; it's an experience crafted to ignite
            your senses and transport you to a bygone era, all while seated at our
            elegant bar top. Join us on this flavorful journey where every bite
            and sip tells a story of creativity, tradition, and the art of mixology.
            :violet[**#CaliforniaRoll #CraftCocktail #SpeakeasyVibes #BarTopTales
            #SushiAdventure #CocktailCraft #EpicureanJourney #FoodieEscape #SavorTheFlavor**]""",

            """🥣💕 WHY I LOVE THIS RECIPE: Arroz Caldo 🍲 There's nothing quite
                like the soothing warmth of a hearty bowl of Arroz Caldo, especially
                on those days when you need a hug from the inside. It's the Filipino version
                of chicken soup for the soul! The zing of fresh ginger in every spoonful makes
                it not just comforting but also incredibly flavorful. Made with love, homemade
                chicken stock, and the simplest of ingredients, this dish is a testament to the magic
                that happens in the kitchen with a little patience and a lot of heart.
                Swipe left for the full recipe and let the cooking begin!\n\n:violet[**🌿🍋 #KitchenTales
                #ComfortFood #ArrozCaldo #ChickenCongee
                #ComfortFood #Homemade #CookingLove #GingerFlavor #Foodie #InstaFood
                #RecipeOfTheDay #Foodstagram #Yum #Delicious #HeartyMeal
                #SoulFood #FoodLovers #EatWell #HomeCooking #FoodPhotography**]""",
            """🍔 Burger Bliss at Friendly's Bar and Grill! 🍔 My friend and
            I stumbled upon this gem and let me just say, it was love at first bite.
            The burger was juicy, flavorful, and cooked to perfection. 🍟 The fries?
            Golden and crispy on the outside, soft and fluffy on the inside - exactly
            how I like them. And the Guinness? Ice cold, just the way it should be.
            🍺 The staff went above and beyond to ensure we had a fantastic experience.
            Can't wait to go back for another round! 🙌\n\n:violet[#BurgerLove #FriendlysFind
            #FoodieAdventures #GuinnessGlow #FryDayEveryday]"""
        ]

        new_images_list = [
            ["./resources/new_images/speakeasy_story.png", "./resources/new_images/speakeasy_square.png"],
            ["./resources/new_images/arroz_story.png", "./resources/new_images/arroz_square.png"],
            ["./resources/new_images/burger_story.png", "./resources/new_images/burger_square.png"]
        ]

        selected_prompt = st.selectbox(
            "Select an example", [f"Example {i+1}" for i in range(len(prompts_list))]
        )

        # Display the corresponding generated post
        if selected_prompt:
            st.markdown("##### Prompt:")
            st.markdown(prompts_list[int(selected_prompt[-1]) - 1])
            st.text("")
            st.markdown("##### Generated Post:")
            st.markdown(posts_list[int(selected_prompt[-1]) - 1])
            st.text("")
            st.text("")

            # Create two columns, one to display the original image and one to display the generated image
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.markdown("##### Original Image:")
                if original_images_list[int(selected_prompt[-1]) - 1]:
                    st.image(original_images_list[int(selected_prompt[-1]) - 1], width=300)
                else:
                    st.markdown(":red[**No image was provided.  We generated one!**]")

            with col2:
                st.markdown("##### Generated Images (Stories, Square):")
                for image in new_images_list[int(selected_prompt[-1]) - 1]:
                    st.image(image, width=300)
        st.text("")
        back_to_home = st.button("Back to Home", type="primary", use_container_width=True)
        if back_to_home:
            switch_page("dalle3_main")

if __name__ == "__main__":
    main()
