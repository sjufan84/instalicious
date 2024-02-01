""" Example posts for users to get inspiration from """
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(
    page_title="DALL-E 2 Examples", page_icon=":camera_flash:",
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
            "fresh strawberries are in season  - can't wait to make pie!",
            """Went to a new Italian restaurant last night in Hollywood
            - had the pizza. Dough was great. I can see this place would be great on Valentine's Day.""",
            """Make me cupcakes for the superbowl - make them themed kansas city
            and then also san francisco 49ers themed."""
        ]

        original_images_list = [
            "./resources/original_images/strawberries.png", "./resources/original_images/pizza_original.png",
            None
        ]

        posts_list = [
            """#### 🍓 Fresh Strawberry Season Alert! 🍓\n The moment we've all been waiting
            for is officially here - fresh strawberry season!
            And what better way to celebrate than with a classic, homemade strawberry pie? 🥧\n ##### Here's a\
            simple yet delicious recipe to make your taste buds dance with the flavors\
            of the season:\n ######  Ingredients:\n - 1 lb fresh strawberries,\
            hulled and halved\n - 1 prebaked pie crust\n - 1 cup sugar\n - 3 tablespoons\
            cornstarch\n - 1/2 cup water\n ###### Directions:\n 1. In a saucepan,\
            mix sugar, cornstarch, and water until smooth.\
            Bring to a boil; cook and stir until thickened, about 2 minutes.\n 2. Add half\
            of the strawberries to the saucepan. Mash and mix well.\
            Pour into the pie crust.\n 3. Arrange the remaining strawberries,\
            cut side down, over the filling.\n 4. Chill for at least 3 hours before serving.\
            Garnish with whipped cream if desired.\n\n Can't wait to see your creations!\
            Don't forget to tag us in your posts and stories. Let's make this strawberry\
            season the sweetest one yet! 🍓💕\n\n **#StrawberryLovers,**\
            are you ready to dive into this pie-making adventure?\n\n **#StrawberrySeason
            #HomemadePie #FreshStrawberries\
            #PieRecipe #Foodie #CookingTime #DessertLovers #StrawberryLovers**
            """,
            """Last night's adventure led me to a hidden gem in Hollywood
            - an Italian restaurant that's like a slice of Italy itself.
            🍕✨ The star of the evening? Their pizza! Imagine biting
            into the most divine dough, perfectly crisp yet tender,
            a true testament to the chef's mastery. But what really sets
            this place apart is its romantic ambiance, making it the perfect spot
            for Valentine's Day. 💑🌹 If you're ever in the area and craving authentic
            Italian flavors, this is the place to be. Trust me, it's more than just a meal;
            it's an experience.\n\n :violet[**#FoodieAdventures #PizzaLovers #HollywoodEats
            #ValentinesDayIdeas #ItalianCuisine #CulinaryJourney #PizzaNight**]""",

            """🏈🧁 Super Bowl Showdown in Cupcake Form! 🧁🏈
            Dive into the Super Bowl spirit with our special edition cupcakes,
            where Kansas City meets San Francisco 49ers - in flavor and style!
            Whether you're rooting for the dynamic Chiefs or the powerhouse 49ers,
            we've got your taste buds covered. From the bold reds and golds of the 49ers
            to the vibrant Chiefs' crimson and yellow, each cupcake is a mini masterpiece.
            #SuperBowlSnacks #SweetGameDay 🤤 Swipe left to pick your team - are you
            Team Kansas City with its mouthwatering BBQ-flavor infused frosting
            or Team San Francisco, boasting a sourdough base and gold rush chocolate topping?
            No matter the victor, these cupcakes are sure to win big at your Super Bowl party!
            Score big in flavor and team spirit. 🎉🏆 Let us know your team in the comments!
            📣 #TeamChiefs or #Team49ers? 🏈\n\n :violet[**#SuperBowlSnacks #SweetGameDay #TeamChiefs\
            #Team49ers #CupcakeShowdown #BakingEndZone #FoodieTouchdown #GameDayTreats**]"""
        ]

        new_images_list = [
            [
                "./resources/new_images/strawberry1.png", "./resources/new_images/strawberry2.png"
            ],
            [
                "./resources/new_images/new_pizza1.png", "./resources/new_images/new_pizza2.png",
                "./resources/new_images/new_pizza3.png"
            ],
            [
                "./resources/new_images/cupcakes1.png",
                "./resources/new_images/cupcakes2.png", "./resources/new_images/cupcakes3.png"
            ]
        ]

        selected_prompt = st.selectbox("Select an", [f"Example {i+1}" for i in range(len(prompts_list))])

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
                    st.markdown(
                        ":red[**No image was provided.  These are generated solely from the prompt!**]"
                    )

            with col2:
                st.markdown("##### Generated Images:")
                for image in new_images_list[int(selected_prompt[-1]) - 1]:
                    st.image(image, width=300)
                # st.image(new_images_list[int(selected_prompt[-1]) - 1], width=300)
        st.text("")
        back_to_home = st.button("Back to Home", type="primary", use_container_width=True)
        if back_to_home:
            switch_page("main")

if __name__ == "__main__":
    main()
