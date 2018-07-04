from CommentControl import CommentControl

def entry_point():
    CC = CommentControl()

    while True:
        username = input('Username: ')
        password = input('Password: ')

        if CC.login(username, password):
           break
        else:
            print("Login failed. Try again\n\n")

    switcher = {'1': lambda : CC.add_comments_by_tag(input('Hashtag: ')), '2' : lambda : CC.add_response(input('Response: ')), '3' : lambda : CC.delete_all_comments(), '4' : lambda : CC.delete_comment(input('Comment id: ')), '5' : lambda : CC.print_comments(), '6' : lambda : CC.print_responses(), '7' : lambda : CC.remove_response(input('Response ID: '))}

    while True:
        try:
            choice = int(input('1. Add comments by hashtag\n2. Add new response to the pool\n3. Delete all comments\n4. Delete individual comment by comment id\n5. View all comments\n6. View responses\n7. Remove response from the pool by id\nEnter 0 to exit\nChoice: '))
            if not choice:
                CC.logout()
                break
            else:
                switcher['{}'.format(choice)]()
        except (ValueError, RuntimeError, TypeError, NameError):
            print("Integer in range expected!")

entry_point()