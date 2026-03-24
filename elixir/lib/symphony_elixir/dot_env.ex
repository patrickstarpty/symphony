defmodule SymphonyElixir.DotEnv do
  @moduledoc """
  Loads environment variables from `.env` files.

  Variables are set only when they are not already present in the
  environment, so explicit exports always take precedence.
  """

  require Logger

  @spec load_from_directory(String.t()) :: :ok
  def load_from_directory(directory) do
    path = Path.join(directory, ".env")

    if File.regular?(path) do
      load_file(path)
    else
      :ok
    end
  end

  @spec load_file(String.t()) :: :ok
  def load_file(path) do
    path
    |> File.stream!()
    |> Stream.map(&String.trim/1)
    |> Stream.reject(&skip_line?/1)
    |> Stream.map(&parse_line/1)
    |> Stream.filter(&match?({:ok, _, _}, &1))
    |> Enum.each(fn {:ok, key, value} ->
      if is_nil(System.get_env(key)) do
        System.put_env(key, value)
      end
    end)
  end

  defp skip_line?(""), do: true
  defp skip_line?("#" <> _), do: true
  defp skip_line?(_), do: false

  @spec parse_line(String.t()) :: {:ok, String.t(), String.t()} | :skip
  defp parse_line(line) do
    case String.split(line, "=", parts: 2) do
      [raw_key, raw_value] ->
        key = raw_key |> String.replace(~r/^export\s+/, "") |> String.trim()
        value = raw_value |> String.trim() |> unquote_value()
        {:ok, key, value}

      _ ->
        :skip
    end
  end

  defp unquote_value(value) do
    cond do
      String.starts_with?(value, "\"") and String.ends_with?(value, "\"") ->
        String.slice(value, 1..-2//1)

      String.starts_with?(value, "'") and String.ends_with?(value, "'") ->
        String.slice(value, 1..-2//1)

      true ->
        value
    end
  end
end
