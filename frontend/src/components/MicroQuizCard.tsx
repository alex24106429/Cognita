import React, { useMemo, useState } from 'react';
import { Alert, Badge, Button, Group, Paper, Radio, Stack, Text, ThemeIcon } from '@mantine/core';
import { IconAlertCircle, IconCheck, IconTargetArrow } from '@tabler/icons-react';
import confetti from 'canvas-confetti';

import type { MicroQuiz, ThemePalette } from '../types';
import { playClarificationTone, playSuccessChime, prefersReducedMotion } from '../utils/feedback';

interface Props {
  quiz: MicroQuiz;
  palette: ThemePalette;
  onAnswered?: (correct: boolean) => void;
}

/**
 * Active comprehension checkpoint.
 *
 * Implements retrieval practice with immediate explanatory feedback. Correct
 * answers fire a confetti burst, a soft chime and a pulse ring; incorrect
 * answers are framed as clarification rather than failure, because shame is a
 * documented disengagement trigger for ADHD readers.
 */
export const MicroQuizCard: React.FC<Props> = ({ quiz, palette, onAnswered }) => {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [pulsing, setPulsing] = useState<boolean>(false);

  const selectedOption = useMemo(
    () => quiz.options.find((option) => option.id === selected),
    [quiz.options, selected]
  );

  const isCorrect = Boolean(selectedOption?.is_correct);

  const handleSubmit = () => {
    if (!selected || submitted) return;

    setSubmitted(true);
    const correct = Boolean(quiz.options.find((option) => option.id === selected)?.is_correct);
    onAnswered?.(correct);

    if (correct) {
      setPulsing(true);
      window.setTimeout(() => setPulsing(false), 750);
      playSuccessChime();
      if (!prefersReducedMotion()) {
        confetti({ particleCount: 55, spread: 65, origin: { y: 0.75 }, disableForReducedMotion: true });
      }
    } else {
      playClarificationTone();
    }
  };

  const handleReset = () => {
    setSubmitted(false);
    setSelected(null);
  };

  return (
    <Paper
      p="md"
      radius="md"
      withBorder
      className={pulsing ? 'cognita-pulse' : undefined}
      style={{ backgroundColor: palette.surface, borderColor: palette.border }}
    >
      <Group justify="space-between" mb="xs" wrap="nowrap">
        <Badge color="teal" variant="filled" leftSection={<IconTargetArrow size={12} />}>
          Active comprehension checkpoint
        </Badge>
        <Badge color="gray" variant="light" size="sm">
          Retrieval practice
        </Badge>
      </Group>

      <Text fw={600} mb="sm">
        {quiz.question}
      </Text>

      <Radio.Group
        value={selected}
        onChange={(value) => {
          if (!submitted) setSelected(value);
        }}
        mb="md"
      >
        <Stack gap="xs">
          {quiz.options.map((option) => {
            const revealCorrect = submitted && option.is_correct;
            const revealWrong = submitted && option.id === selected && !option.is_correct;
            return (
              <Radio
                key={option.id}
                value={option.id}
                disabled={submitted}
                label={`${option.id}) ${option.text}`}
                styles={{
                  label: {
                    fontWeight: revealCorrect ? 700 : 400,
                    color: revealCorrect
                      ? '#2B8A3E'
                      : revealWrong
                        ? '#C92A2A'
                        : palette.text,
                  },
                }}
              />
            );
          })}
        </Stack>
      </Radio.Group>

      {!submitted ? (
        <Button size="xs" color="teal" onClick={handleSubmit} disabled={!selected}>
          Check answer
        </Button>
      ) : (
        <Stack gap="xs">
          <Alert
            icon={
              isCorrect ? (
                <IconCheck size={16} />
              ) : (
                <IconAlertCircle size={16} />
              )
            }
            color={isCorrect ? 'green' : 'orange'}
            title={isCorrect ? 'Accurate — retention secured' : 'Concept clarification'}
          >
            <Text size="sm">{selectedOption?.feedback}</Text>
            {quiz.explanation && (
              <Text size="xs" mt="xs" fw={500}>
                Explanation: {quiz.explanation}
              </Text>
            )}
          </Alert>

          <Group justify="space-between" align="center">
            <Group gap={6} wrap="nowrap">
              <ThemeIcon
                size="sm"
                radius="xl"
                variant="light"
                color={isCorrect ? 'green' : 'orange'}
              >
                {isCorrect ? <IconCheck size={12} /> : <IconAlertCircle size={12} />}
              </ThemeIcon>
              <Text size="xs" c={palette.mutedText}>
                {isCorrect
                  ? 'Checkpoint cleared. Continue to the next block.'
                  : 'Review the block once more before continuing — no penalty.'}
              </Text>
            </Group>
            <Button size="compact-xs" variant="subtle" color="gray" onClick={handleReset}>
              Try again
            </Button>
          </Group>
        </Stack>
      )}
    </Paper>
  );
};
