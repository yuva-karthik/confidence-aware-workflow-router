from graph import graph


def main():
    print("=" * 60)
    print("              P18 - A ROUTER")
    print("=" * 60)

    print("\nAvailable commands:")
    print("  Type a request to route it")
    print("  'exit' or 'quit' to stop")
    print("-" * 60)

    while True:

        try:
            user_input = input("\nUser: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not user_input:
            print("Please enter a request.")
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        initial_state = {
            "input": user_input,
            "category": None,
            "confidence": None,
            "status": None,
            "result": None
        }

        try:
            result = graph.invoke(initial_state)

            print("\n" + "=" * 60)
            print("ROUTER RESULT")
            print("=" * 60)

            print(
                f"Category   : {result.get('category')}"
            )

            confidence = result.get("confidence")

            if confidence is not None:
                print(
                    f"Confidence : {confidence:.2%}"
                )

            print(
                f"Status     : {result.get('status')}"
            )

            if result.get("workflow"):
                print(
                    f"Workflow   : {result['workflow']}"
                )

            if result.get("result"):
                print("\nAgent Response:")
                print(result["result"])

            print("=" * 60)

        except Exception as e:

            print("\n❌ Router error:")
            print(str(e))


if __name__ == "__main__":
    main()