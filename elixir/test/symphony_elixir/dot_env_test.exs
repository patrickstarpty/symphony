defmodule SymphonyElixir.DotEnvTest do
  use ExUnit.Case, async: false

  alias SymphonyElixir.DotEnv

  @moduletag :tmp_dir

  setup %{tmp_dir: tmp_dir} do
    %{tmp_dir: tmp_dir}
  end

  describe "load_from_directory/1" do
    test "loads .env file and sets env vars", %{tmp_dir: tmp_dir} do
      env_key = "SYMP_DOTENV_TEST_#{System.unique_integer([:positive])}"
      File.write!(Path.join(tmp_dir, ".env"), "#{env_key}=test_value\n")
      on_exit(fn -> System.delete_env(env_key) end)

      assert :ok = DotEnv.load_from_directory(tmp_dir)
      assert System.get_env(env_key) == "test_value"
    end

    test "does not overwrite existing env vars", %{tmp_dir: tmp_dir} do
      env_key = "SYMP_DOTENV_EXISTING_#{System.unique_integer([:positive])}"
      System.put_env(env_key, "original")
      File.write!(Path.join(tmp_dir, ".env"), "#{env_key}=overwritten\n")
      on_exit(fn -> System.delete_env(env_key) end)

      assert :ok = DotEnv.load_from_directory(tmp_dir)
      assert System.get_env(env_key) == "original"
    end

    test "returns :ok when no .env file exists", %{tmp_dir: tmp_dir} do
      assert :ok = DotEnv.load_from_directory(tmp_dir)
    end

    test "skips blank lines and comments", %{tmp_dir: tmp_dir} do
      env_key = "SYMP_DOTENV_COMMENT_#{System.unique_integer([:positive])}"

      content = """
      # This is a comment

      #{env_key}=hello
      # Another comment
      """

      File.write!(Path.join(tmp_dir, ".env"), content)
      on_exit(fn -> System.delete_env(env_key) end)

      assert :ok = DotEnv.load_from_directory(tmp_dir)
      assert System.get_env(env_key) == "hello"
    end

    test "handles quoted values", %{tmp_dir: tmp_dir} do
      key1 = "SYMP_DOTENV_DQ_#{System.unique_integer([:positive])}"
      key2 = "SYMP_DOTENV_SQ_#{System.unique_integer([:positive])}"

      content = """
      #{key1}="double quoted"
      #{key2}='single quoted'
      """

      File.write!(Path.join(tmp_dir, ".env"), content)

      on_exit(fn ->
        System.delete_env(key1)
        System.delete_env(key2)
      end)

      assert :ok = DotEnv.load_from_directory(tmp_dir)
      assert System.get_env(key1) == "double quoted"
      assert System.get_env(key2) == "single quoted"
    end

    test "handles export prefix", %{tmp_dir: tmp_dir} do
      env_key = "SYMP_DOTENV_EXPORT_#{System.unique_integer([:positive])}"
      File.write!(Path.join(tmp_dir, ".env"), "export #{env_key}=exported_val\n")
      on_exit(fn -> System.delete_env(env_key) end)

      assert :ok = DotEnv.load_from_directory(tmp_dir)
      assert System.get_env(env_key) == "exported_val"
    end

    test "handles values containing equals signs", %{tmp_dir: tmp_dir} do
      env_key = "SYMP_DOTENV_EQ_#{System.unique_integer([:positive])}"
      File.write!(Path.join(tmp_dir, ".env"), "#{env_key}=abc=def=ghi\n")
      on_exit(fn -> System.delete_env(env_key) end)

      assert :ok = DotEnv.load_from_directory(tmp_dir)
      assert System.get_env(env_key) == "abc=def=ghi"
    end

    test "skips malformed lines without equals sign", %{tmp_dir: tmp_dir} do
      env_key = "SYMP_DOTENV_GOOD_#{System.unique_integer([:positive])}"

      content = """
      MALFORMED_NO_EQUALS
      #{env_key}=valid
      """

      File.write!(Path.join(tmp_dir, ".env"), content)
      on_exit(fn -> System.delete_env(env_key) end)

      assert :ok = DotEnv.load_from_directory(tmp_dir)
      assert System.get_env(env_key) == "valid"
    end
  end
end
